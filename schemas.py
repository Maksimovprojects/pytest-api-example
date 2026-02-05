pet = {
    "type": "object",
    "required": ["name", "type"],
    "properties": {
        "id": {
            "type": "integer"
        },
        "name": {
            "type": "string"  # : Changed from "integer" to "string"
        },
        "type": {
            "type": "string",
            "enum": ["cat", "dog", "fish"]
        },
        "status": {
            "type": "string",
            "enum": ["available", "sold", "pending"]
        },
    }
}


# Add Order schema
order = {
    "type": "object",
    "required": ["id", "pet_id"],
    "properties": {
        "id": {
            "type": "string"  # UUID string
        },
        "pet_id": {
            "type": "integer"
        },
        "status": {
            "type": "string",
            "enum": ["available", "sold", "pending"]
        }
    }
}