# Task‑Tracker API

A simple task and project management API built with **FastAPI**, **SQLAlchemy (async)**, and **Pydantic v2**.  
Designed as a portfolio project to demonstrate clean architecture, async patterns, and testing best practices.

---

## Features

- **Projects & Tasks**  
  - Create, read, update, and delete tasks  
  - Create and read projects with task relationships  

- **Async SQLAlchemy ORM**  
  - Fully asynchronous DB access with SQLite (dev/test) or PostgreSQL (prod-ready)

- **Pydantic v2 Models**  
  - Data validation and serialization with strict typing

- **Testing**  
  - In‑memory SQLite for fast end‑to‑end tests  
  - `pytest` + `httpx.AsyncClient`

---

## Tech Stack

- **Python** 3.12  
- **FastAPI** 0.115  
- **SQLAlchemy** 2.x (async)  
- **Pydantic** v2  
- **Poetry** (dependency management)
