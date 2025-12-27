# Simple MongoDB Setup

A single script to run MongoDB locally with Docker.

## Quick Start

```bash
# Start MongoDB
./mongodb.sh

# Open MongoDB shell
./mongodb.sh shell

# Stop MongoDB
./mongodb.sh stop
```

## Connection Details

- **Host**: localhost
- **Port**: 27017
- **Username**: admin
- **Password**: (set in mongodb.sh script, default: password123)
- **Database**: the_data_packet (used by The Data Packet application)

**Connection URL**:
```
mongodb://admin:password123@localhost:27017/the_data_packet?authSource=admin
```

## What MongoDB Stores

When integrated with The Data Packet, MongoDB stores:

### Articles Collection
- **Purpose**: Prevents reusing articles in future episodes
- **Data**: Article URLs, titles, publication dates, sources
- **Benefit**: Ensures each podcast episode has unique content

### Episodes Collection  
- **Purpose**: Episode tracking and analytics
- **Data**: Episode metadata, execution times, success status, file paths
- **Benefit**: Complete audit trail of podcast generation history

## Usage Examples

**Python**:
```python
from pymongo import MongoClient
client = MongoClient('mongodb://admin:password123@localhost:27017/the_data_packet?authSource=admin')
db = client.the_data_packet

# View used articles
articles = list(db.articles.find())
print(f"Total articles used: {len(articles)}")

# View episode history  
episodes = list(db.episodes.find())
print(f"Total episodes generated: {len(episodes)}")
```

**MongoDB Shell**:
```javascript
// Switch to the database
use the_data_packet

// Show collections
show collections

// Count documents
db.articles.countDocuments()
db.episodes.countDocuments()

// View recent episodes
db.episodes.find().sort({"_id": -1}).limit(5)
```

## Commands

- `./mongodb.sh start` - Start MongoDB
- `./mongodb.sh stop` - Stop MongoDB  
- `./mongodb.sh shell` - Open MongoDB shell
- `./mongodb.sh logs` - View logs
- `./mongodb.sh status` - Check status
- `./mongodb.sh remove` - Remove everything (including data)