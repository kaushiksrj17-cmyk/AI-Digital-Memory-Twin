# ECHO Knowledge Graph Architecture

## 1. Overview

The **ECHO Knowledge Graph** constructs an interconnected topological network of verified entities, memories, milestones, locations, and documents.

Compatibility:
- Production target: **Neo4j** (via Cypher queries and graph database driver).
- Local / Test fallback: **LocalGraphStore** (in-memory adjacency with SQLite persistence hooks), enabling zero-dependency offline local development and test runs.

---

## 2. Supported Node Types

The graph models 10 distinct entity classes:

1. `PERSON`: Memorial subject, family members, friends, colleagues.
2. `MEMORY`: Preserved recollection units from Phase 2 Vault.
3. `EVENT`: Documented milestones, celebrations, ceremonies.
4. `PLACE`: Geographic locations, birthplaces, residences, cities.
5. `OBJECT`: Documented heirlooms, tools, vehicles, books, keepsakes.
6. `DOCUMENT`: Archival diplomas, letters, certificates, journals.
7. `MEDIA`: Original photographs, audio tapes, video reels.
8. `ORGANIZATION`: Universities, employers, guilds, clubs.
9. `DATE`: Documented historical years, months, days.
10. `TOPIC`: Subject matter topics, research fields, artistic themes.

---

## 3. Supported Directed Edges

All relationships are directed and require explicit evidence citations:

- `PERSON -> RELATED_TO -> PERSON`
- `PERSON -> APPEARED_IN -> MEMORY`
- `PERSON -> PARTICIPATED_IN -> EVENT`
- `PERSON -> ASSOCIATED_WITH -> PLACE`
- `PERSON -> OWNED_OR_USED -> OBJECT`
- `MEMORY -> DOCUMENTS -> EVENT`
- `MEMORY -> CONTAINS -> MEDIA`
- `MEDIA -> PROVIDES_EVIDENCE_FOR -> MEMORY`
- `EVENT -> OCCURRED_AT -> PLACE`
- `EVENT -> INVOLVES -> PERSON`
- `EVENT -> OCCURRED_ON -> DATE`
- `PERSON -> STUDIED_AT -> ORGANIZATION`
- `PERSON -> WORKED_AT -> ORGANIZATION`
- `PERSON -> INTERESTED_IN -> TOPIC`
- `MEMORY -> ABOUT -> TOPIC`
- `OBJECT -> APPEARS_IN -> MEMORY`
- `PERSON -> MET -> PERSON`

---

## 4. Graph Safety Principle

> [!CAUTION]
> **Anti-Co-occurrence Inference Rule**:
> Merely observing two entities (e.g. "Arthur" and "Edinburgh") in the same document does **NOT** establish a `LIVES_IN` or `EMPLOYED_AT` relationship.
> Relationships are created strictly when supported by explicit syntactic extractions or user-verified primary evidence.

---

## 5. Knowledge Graph Integration in Phase 5 RAG
In Phase 5, the conversation engine leverages graph traversal for relational and kinship inquiries (e.g., *"What was the relationship between Arthur and Mary?"*). The `ContextManager` queries the graph for connecting edges, verifies source evidence backing each edge, and provides triples (`Subject --[Predicate]--> Object`) to the prompt engine. Relationships lacking evidentiary backing are never returned as verified facts.
