# History Crusher Telegram Bot (ITMO Course Project)

## Overview

This project is a Telegram bot developed using Python and the `aiogram` framework. It's designed as a personal tool to help users memorize historical dates through interactive quizzes. It also includes a simple real-time PvP 'Fight' mode where two users compete to answer date questions faster and more accurately.

**Important Context:** This bot was created as a student project for a history course at **ITMO University**. Its primary purpose is to serve as a **demonstration of my coding skills** and practices in areas such as:

*   Asynchronous programming with `asyncio` and `aiogram`.
*   Database interaction using `SQLAlchemy` (with PostgreSQL) and `Alembic` for migrations.
*   Dependency management and project structuring.
*   State management using `aiogram`'s FSM with Redis.
*   Containerization with `Docker` and `Docker Compose`.
*   Basic CI/CD setup using GitHub Actions for Docker image publishing.

**This project is not intended for widespread public use or as a production-ready application.** It's showcased here as part of my personal portfolio on GitHub.

## Features

*   **User Management:** Basic user registration upon first interaction. Admin role differentiation.
*   **Personal Questions:** Users can create their own questions with associated dates (Year, Month-Year, Day-Month-Year).
*   **Quiz Mode (`/test`):**
    *   Fetches random questions (prioritizing user's own questions, considering answer history/weight, optionally including public questions).
    *   Accepts text-based answers and attempts to parse the date.
    *   If the text answer is incorrect, it generates multiple-choice options (distractors) including the correct answer.
    *   Adapts question `weight` based on user's answer history (using concepts like boosting for newer/less-answered questions).
*   **PvP Fight Mode:**
    *   Players can initiate a fight and wait for an opponent.
    *   Matchmaking places waiting players into a 1v1 session if another player joins within the timeout.
    *   Rounds present a random *public* date question to both players simultaneously after a short countdown.
    *   Players answer via text message within a time limit (invalid dates are rejected, messages are deleted).
    *   Answers are scored based on proximity to the correct date (closer = higher score).
    *   The player with the lower score takes damage proportional to the score difference for that round.
    *   The game continues until one player's health is depleted or a mutual timeout occurs in a round.
    *   Uses asynchronous timers for matchmaking, round countdowns, and answer deadlines.
*   **Public Questions:** Admins can create "public" questions available to all users who opt-in (used in both `/test` and `/fight`).
*   **Question Management:** Users can list and delete their own questions. Admins can manage public questions (CRUD).
*   **User Settings:**
    *   Customize the number of multiple-choice options presented in `/test` mode.
    *   Enable/disable receiving public questions during quizzes (`/test`).
*   **Admin Panel:**
    *   View a list of registered users (paginated).
    *   Manage public questions.
    *   Basic user mailing functionality (send a message to all registered users).
*   **State Management:** Uses `aiogram`'s Finite State Machine (FSM) persisted in Redis for multi-step operations like question creation or the standard testing flow. (Fight mode uses a separate in-memory manager).
*   **Database Interaction:** Uses SQLAlchemy ORM with an async driver (`asyncpg`) for interacting with a PostgreSQL database. Repositories pattern is used for data access logic.
*   **Deployment Ready:** Includes `Dockerfile` and `docker-compose.yml` for easy containerized deployment. GitHub Actions workflow automates Docker image building and pushing to GitHub Container Registry (GHCR) on release.

## Technology Stack

*   **Language:** Python 3.10
*   **Telegram Bot Framework:** `aiogram` 3.x
*   **Database:** PostgreSQL
*   **ORM & Migrations:** `SQLAlchemy` 2.x, `Alembic`
*   **Async DB Driver:** `asyncpg`
*   **Caching/FSM Storage:** Redis
*   **Data Validation:** `Pydantic`
*   **Containerization:** Docker, Docker Compose
*   **CI/CD:** GitHub Actions

## Disclaimer

As mentioned, this is a student project and a portfolio piece. It may lack features, extensive error handling, security hardening, or user support typically expected from a production application. Use it as a reference for code structure and feature implementation examples within the `aiogram` ecosystem.
