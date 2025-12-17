"""RSS feed generation and management for podcast episodes."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from the_data_packet.core.config import Config, get_config
from the_data_packet.core.exceptions import TheDataPacketError
from the_data_packet.core.logging import get_logger
from the_data_packet.sources.base import Article
from the_data_packet.utils.s3 import S3Storage, S3UploadResult

logger = get_logger(__name__)


@dataclass
class PodcastEpisode:
    """Represents a podcast episode for RSS feed."""

    title: str
    description: str
    audio_url: str
    pub_date: datetime
    episode_number: Optional[int] = None
    duration: Optional[str] = None  # Format: "HH:MM:SS"
    file_size: Optional[int] = None  # In bytes
    guid: Optional[str] = None
    author: Optional[str] = None

    def __post_init__(self) -> None:
        """Generate GUID if not provided."""
        if not self.guid:
            # Generate unique GUID based on title and date
            date_str = self.pub_date.strftime("%Y%m%d")
            self.guid = f"{date_str}-{self.title.lower().replace(' ', '-')}"


@dataclass
class RSSGenerationResult:
    """Result of RSS feed generation."""

    success: bool = False
    rss_content: Optional[str] = None
    local_path: Optional[Path] = None
    s3_url: Optional[str] = None
    error_message: Optional[str] = None


class RSSGenerator:
    """Generates and manages RSS feeds for podcast episodes."""

    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize RSS generator."""
        self.config = config or get_config()
        self.s3_storage: Optional[S3Storage] = None

    def _get_next_episode_number(self, existing_episodes: List[PodcastEpisode]) -> int:
        """Determine the next episode number based on existing episodes."""
        if not existing_episodes:
            return 1

        # Find the highest episode number
        max_episode = 0
        for episode in existing_episodes:
            if episode.episode_number and episode.episode_number > max_episode:
                max_episode = episode.episode_number

        return max_episode + 1

    def generate_episode_from_articles(
        self,
        articles: List[Article],
        audio_url: str,
        episode_number: Optional[int] = None,
        duration: Optional[str] = None,
        file_size: Optional[int] = None,
        existing_episodes: Optional[List[PodcastEpisode]] = None,
    ) -> PodcastEpisode:
        """Generate a podcast episode from articles."""
        # Auto-determine episode number if not provided
        if episode_number is None:
            if existing_episodes is None:
                # Try to load existing episodes from S3 if available
                if self._should_use_s3():
                    existing_feed = self._download_existing_rss()
                    if existing_feed:
                        existing_episodes = self.load_existing_feed(existing_feed)
                    else:
                        existing_episodes = []
                else:
                    existing_episodes = []
            episode_number = self._get_next_episode_number(existing_episodes)

        # Get current date for title formatting
        pub_date = datetime.now()
        day = pub_date.day
        ordinal_suffix = self._get_ordinal_suffix(day)
        date_str = pub_date.strftime(f"%b {day}{ordinal_suffix}, %Y")

        # Create episode title with date
        title = f"Episode {episode_number} - {date_str}"

        # Create description from articles
        description_parts = []
        for i, article in enumerate(articles, 1):
            if len(articles) > 1:
                description_parts.append(f"{i}. {article.title}")
            else:
                description_parts.append(article.title)
            if article.url:
                description_parts.append(f"   Source: {article.url}")
            if i < len(articles):
                description_parts.append("")

        description = "\n".join(description_parts)

        return PodcastEpisode(
            title=title,
            description=description,
            audio_url=audio_url,
            pub_date=datetime.now(),
            episode_number=episode_number,
            duration=duration,
            file_size=file_size,
            author=self.config.show_name,
        )

    def generate_rss_feed(
        self,
        episodes: List[PodcastEpisode],
        channel_title: Optional[str] = None,
        channel_description: Optional[str] = None,
        channel_link: Optional[str] = None,
        channel_image_url: Optional[str] = None,
        channel_email: Optional[str] = None,
    ) -> str:
        """Generate complete RSS feed XML."""
        # Create RSS root element
        rss = ET.Element("rss", version="2.0")
        rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")

        # Create channel
        channel = ET.SubElement(rss, "channel")

        # Channel metadata
        ET.SubElement(channel, "title").text = channel_title or self.config.show_name
        ET.SubElement(channel, "description").text = (
            channel_description
            or f"{self.config.show_name} - Your source for the latest tech news and insights"
        )
        ET.SubElement(channel, "link").text = (
            channel_link or "https://github.com/TheWinterShadow/The-Data-Packet"
        )

        # Add email contact if provided
        email = channel_email or self.config.rss_channel_email
        if email:
            ET.SubElement(channel, "managingEditor").text = (
                f"{email} ({self.config.show_name})"
            )
            ET.SubElement(channel, "webMaster").text = (
                f"{email} ({self.config.show_name})"
            )

        ET.SubElement(channel, "language").text = "en-us"
        ET.SubElement(channel, "lastBuildDate").text = self._format_rfc822_date(
            datetime.now()
        )
        ET.SubElement(channel, "pubDate").text = self._format_rfc822_date(
            datetime.now()
        )
        ET.SubElement(channel, "generator").text = "The Data Packet RSS Generator"

        # iTunes specific tags
        ET.SubElement(channel, "itunes:subtitle").text = "Tech news and insights"
        ET.SubElement(channel, "itunes:author").text = self.config.show_name
        ET.SubElement(channel, "itunes:summary").text = (
            channel_description
            or f"{self.config.show_name} - Your source for the latest tech news and insights"
        )
        ET.SubElement(channel, "itunes:explicit").text = "no"

        # iTunes owner information (requires email)
        if email:
            itunes_owner = ET.SubElement(channel, "itunes:owner")
            ET.SubElement(itunes_owner, "itunes:name").text = self.config.show_name
            ET.SubElement(itunes_owner, "itunes:email").text = email

        # iTunes category
        itunes_category = ET.SubElement(channel, "itunes:category", text="Technology")

        # Channel image and iTunes cover art
        image_url = channel_image_url or self.config.rss_channel_image_url
        if image_url:
            # Standard RSS image
            image = ET.SubElement(channel, "image")
            ET.SubElement(image, "url").text = image_url
            ET.SubElement(image, "title").text = channel_title or self.config.show_name
            ET.SubElement(image, "link").text = channel_link or ""
            # iTunes recommended size
            ET.SubElement(image, "width").text = "1400"
            ET.SubElement(image, "height").text = "1400"

            # iTunes cover art
            ET.SubElement(channel, "itunes:image", href=image_url)

        # Add episodes
        for episode in sorted(episodes, key=lambda x: x.pub_date, reverse=True):
            self._add_episode_to_channel(channel, episode)

        # Generate XML string
        self._indent_xml(rss)
        xml_str = ET.tostring(rss, encoding="unicode", xml_declaration=True)

        return xml_str

    def _get_ordinal_suffix(self, day: int) -> str:
        """Get ordinal suffix for day (1st, 2nd, 3rd, 4th, etc.)."""
        if 10 <= day % 100 <= 20:
            return "th"
        else:
            return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    def _add_episode_to_channel(
        self, channel: ET.Element, episode: PodcastEpisode
    ) -> None:
        """Add episode item to RSS channel."""
        item = ET.SubElement(channel, "item")

        ET.SubElement(item, "title").text = episode.title
        ET.SubElement(item, "description").text = episode.description
        ET.SubElement(item, "link").text = episode.audio_url
        ET.SubElement(item, "guid").text = episode.guid
        ET.SubElement(item, "pubDate").text = self._format_rfc822_date(episode.pub_date)

        # Enclosure (audio file)
        enclosure_attrs = {"url": episode.audio_url, "type": "audio/mpeg"}
        if episode.file_size:
            enclosure_attrs["length"] = str(episode.file_size)
        ET.SubElement(item, "enclosure", enclosure_attrs)

        # iTunes specific tags
        ET.SubElement(item, "itunes:subtitle").text = episode.title
        ET.SubElement(item, "itunes:summary").text = episode.description
        if episode.author:
            ET.SubElement(item, "itunes:author").text = episode.author
        if episode.duration:
            ET.SubElement(item, "itunes:duration").text = episode.duration
        if episode.episode_number:
            ET.SubElement(item, "itunes:episode").text = str(episode.episode_number)

    def load_existing_feed(self, rss_content: str) -> List[PodcastEpisode]:
        """Parse existing RSS feed and extract episodes."""
        try:
            root = ET.fromstring(rss_content)
            episodes = []

            # Find all item elements
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                description_elem = item.find("description")
                enclosure_elem = item.find("enclosure")
                guid_elem = item.find("guid")
                pub_date_elem = item.find("pubDate")
                duration_elem = item.find(
                    "itunes:duration",
                    {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"},
                )
                episode_num_elem = item.find(
                    "itunes:episode",
                    {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"},
                )
                author_elem = item.find(
                    "itunes:author",
                    {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"},
                )

                if title_elem is not None and enclosure_elem is not None:
                    # Parse episode number from title if not in iTunes tag
                    episode_number = None
                    if episode_num_elem is not None and episode_num_elem.text:
                        try:
                            episode_number = int(episode_num_elem.text)
                        except (ValueError, TypeError):
                            pass

                    # Parse publication date
                    pub_date = datetime.now()
                    if pub_date_elem is not None and pub_date_elem.text:
                        try:
                            pub_date = datetime.strptime(
                                pub_date_elem.text, "%a, %d %b %Y %H:%M:%S %z"
                            ).replace(tzinfo=None)
                        except ValueError:
                            pass

                    # Parse file size
                    file_size = None
                    length_attr = enclosure_elem.get("length")
                    if length_attr:
                        try:
                            file_size = int(length_attr)
                        except (ValueError, TypeError):
                            pass

                    episode = PodcastEpisode(
                        title=title_elem.text if title_elem.text else "",
                        description=(
                            description_elem.text
                            if description_elem is not None and description_elem.text
                            else ""
                        ),
                        audio_url=enclosure_elem.get("url", ""),
                        pub_date=pub_date,
                        episode_number=episode_number,
                        duration=(
                            duration_elem.text
                            if duration_elem is not None and duration_elem.text
                            else None
                        ),
                        file_size=file_size,
                        guid=guid_elem.text if guid_elem is not None else None,
                        author=(
                            author_elem.text
                            if author_elem is not None and author_elem.text
                            else None
                        ),
                    )
                    episodes.append(episode)

            logger.info(f"Loaded {len(episodes)} episodes from existing RSS feed")
            return episodes

        except ET.ParseError as e:
            logger.error(f"Failed to parse RSS feed: {e}")
            return []

    def update_rss_feed(self, new_episode: PodcastEpisode) -> RSSGenerationResult:
        """Update RSS feed with new episode."""
        result = RSSGenerationResult()

        try:
            # Load existing episodes from S3
            existing_episodes = []
            if self._should_use_s3():
                existing_feed = self._download_existing_rss()
                if existing_feed:
                    existing_episodes = self.load_existing_feed(existing_feed)

            # Auto-assign episode number if not already set
            if not new_episode.episode_number:
                new_episode.episode_number = self._get_next_episode_number(
                    existing_episodes
                )
                # Update the title with the correct episode number
                pub_date = new_episode.pub_date
                day = pub_date.day
                ordinal_suffix = self._get_ordinal_suffix(day)
                date_str = pub_date.strftime(f"%b {day}{ordinal_suffix}, %Y")
                new_episode.title = f"Episode {new_episode.episode_number} - {date_str}"

            # Add new episode to the beginning
            all_episodes = [new_episode] + existing_episodes

            # Keep only the latest N episodes (configurable)
            max_episodes = getattr(self.config, "max_rss_episodes", 50)
            all_episodes = all_episodes[:max_episodes]

            # Generate new RSS feed with proper metadata
            rss_content = self.generate_rss_feed(
                episodes=all_episodes,
                channel_title=self.config.rss_channel_title,
                channel_description=self.config.rss_channel_description,
                channel_link=self.config.rss_channel_link,
                channel_image_url=self.config.rss_channel_image_url,
                channel_email=self.config.rss_channel_email,
            )
            result.rss_content = rss_content

            # Save locally
            local_path = self._save_rss_locally(rss_content)
            result.local_path = local_path

            # Upload to S3
            if self._should_use_s3():
                s3_result = self._upload_rss_to_s3(local_path)
                if s3_result.success:
                    result.s3_url = s3_result.s3_url
                    logger.info(f"RSS feed updated successfully: {s3_result.s3_url}")
                else:
                    logger.warning(
                        f"Failed to upload RSS to S3: {s3_result.error_message}"
                    )

            result.success = True

        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Failed to update RSS feed: {e}")

        return result

    def _download_existing_rss(self) -> Optional[str]:
        """Download existing RSS feed from S3."""
        if not self.s3_storage:
            self.s3_storage = S3Storage()

        rss_key = f"{self.config.show_name.lower().replace(' ', '-')}/feed.xml"

        try:
            response = self.s3_storage.s3_client.get_object(
                Bucket=self.s3_storage.bucket_name, Key=rss_key
            )
            content: str = response["Body"].read().decode("utf-8")
            logger.info("Downloaded existing RSS feed from S3")
            return content

        except Exception as e:
            logger.info(f"No existing RSS feed found in S3 (or error downloading): {e}")
            return None

    def _save_rss_locally(self, rss_content: str) -> Path:
        """Save RSS feed to local file."""
        # Ensure output directory exists
        self.config.output_directory.mkdir(parents=True, exist_ok=True)

        # Generate filename
        rss_filename = f"{self.config.show_name.lower().replace(' ', '-')}_feed.xml"
        rss_path = self.config.output_directory / rss_filename

        try:
            with open(rss_path, "w", encoding="utf-8") as f:
                f.write(rss_content)

            logger.info(f"RSS feed saved locally to {rss_path}")
            return rss_path

        except Exception as e:
            raise TheDataPacketError(f"Failed to save RSS feed: {e}")

    def _upload_rss_to_s3(self, rss_path: Path) -> S3UploadResult:
        """Upload RSS feed to S3."""
        if not self.s3_storage:
            self.s3_storage = S3Storage()

        # Use consistent S3 key for RSS feed
        rss_key = f"{self.config.show_name.lower().replace(' ', '-')}/feed.xml"

        return self.s3_storage.upload_file(
            rss_path, rss_key, content_type="application/rss+xml"
        )

    def _should_use_s3(self) -> bool:
        """Check if S3 should be used for uploads."""
        return bool(self.config.s3_bucket_name and self.config.aws_access_key_id)

    def _format_rfc822_date(self, dt: datetime) -> str:
        """Format datetime as RFC 822 date string."""
        return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

    def _indent_xml(self, elem: ET.Element, level: int = 0) -> None:
        """Add indentation to XML for pretty printing."""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent_xml(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
