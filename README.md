<!-- Personal portfolio. SVG artwork lives in assets/. -->
<p align="center">
  <img src="assets/sr-hero.svg" width="100%" alt="Shaxriyor Raximov — Software Engineer / Java Backend Engineer. APIs, events, and connected systems.">
</p>

<p align="center">
  <a href="https://github.com/RahimovShaxriyor?tab=repositories"><b>Explore my work ↗</b></a> &nbsp; · &nbsp;
  <a href="https://t.me/raximovshaxriyor"><b>Telegram</b></a> &nbsp; · &nbsp;
  <a href="mailto:rahimov55shah@gmail.com"><b>Get in touch</b></a>
</p>

### Behind the systems

I’m **Shaxriyor**, a software engineer working with **Java and Spring Boot**. I build APIs, connect services, and work through the details that make systems reliable: authentication, relational data, asynchronous events, and containerized infrastructure.

With **React and TypeScript**, I bring that work into usable interfaces. My projects connect backend engineering with the experience on the other side of the API.

<br>

## Selected work

<a href="https://github.com/RahimovShaxriyor/hotelos-microservices">
  <img src="assets/hotelos-cover.svg" width="100%" alt="HotelOS — event-driven backend for connected hotel operations. Java, Spring Boot, RabbitMQ. Open repository.">
</a>

**Java 17 · Spring Boot · PostgreSQL · RabbitMQ · Flyway**

**Architecture & problem** · Separate hotel operations into bounded contexts. Row-level locking coordinates concurrent room allocation; a transactional outbox with publisher confirms handles event delivery.

**Implementation outcome** · Independent room-state axes and correlated turnover events support the reception-to-housekeeping lifecycle, with WebSocket updates for the operations dashboard.

[**Explore HotelOS ↗**](https://github.com/RahimovShaxriyor/hotelos-microservices) &nbsp; · &nbsp; [Architecture](https://github.com/RahimovShaxriyor/hotelos-microservices#architecture) &nbsp; · &nbsp; [Activity](https://github.com/RahimovShaxriyor/hotelos-microservices/commits/main)

<br>

<a href="https://github.com/RahimovShaxriyor/cloudeware-pro">
  <img src="assets/cloudware-cover.svg" width="100%" alt="CloudWare Pro — full-stack wholesale management demo. Spring Boot, React, PostgreSQL. Open repository.">
</a>

**Java 17 · Spring Boot · Spring JDBC · React / TypeScript · PostgreSQL · Nginx**

**Architecture & problem** · Route wholesale workflows across seven domain services through Nginx, with a shared Java module and a React SPA.

**Implementation outcome** · Products, inventory, customer orders, and payments are connected through one interface and a reproducible Docker Compose environment. This remains a demonstration application, without a verified production SLA.

[**Explore CloudWare Pro ↗**](https://github.com/RahimovShaxriyor/cloudeware-pro) &nbsp; · &nbsp; [Architecture](https://github.com/RahimovShaxriyor/cloudeware-pro/blob/main/docs/ARCHITECTURE.md) &nbsp; · &nbsp; [Activity](https://github.com/RahimovShaxriyor/cloudeware-pro/commits/main)

<br>

<a href="https://github.com/RahimovShaxriyor/ExampleWeb-Redis">
  <img src="assets/redis-cover.svg" width="100%" alt="Redis Visual Demo — an interactive data and caching lab. Java, Spring Data Redis, Docker. Open repository.">
</a>

**Java 17 · Spring Boot · Spring Data Redis · Redis 7 · Docker Compose**

**Architecture & problem** · A browser UI calls a Spring service backed by `StringRedisTemplate`, making temporary data and Redis operations observable.

**Implementation outcome** · Interactive examples of key expiry, atomic increments, and courier-state hashes. A focused learning lab; it does not claim measured database-load reductions or production scale.

[**Explore Redis Visual Demo ↗**](https://github.com/RahimovShaxriyor/ExampleWeb-Redis) &nbsp; · &nbsp; [Implementation](https://github.com/RahimovShaxriyor/ExampleWeb-Redis/blob/main/src/main/java/org/gatewayservice/RedisDemoService.java) &nbsp; · &nbsp; [Activity](https://github.com/RahimovShaxriyor/ExampleWeb-Redis/commits/main)

<br>

## Engineering Activity

Profile-wide activity, with repository-level evidence below. Counts describe GitHub activity; they are not a code-quality or productivity score.

<picture>
  <source media="(max-width: 640px) and (prefers-color-scheme: dark)" srcset="assets/engineering/activity-dark-mobile.svg">
  <source media="(max-width: 640px)" srcset="assets/engineering/activity-light-mobile.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/engineering/activity-dark.svg">
  <img src="assets/engineering/activity-light.svg" width="100%" alt="Engineering activity snapshot: contributions, public pull requests, stars on owned public repositories, and contribution streaks. The image states its reporting period and snapshot date.">
</picture>

<sub>365-day contribution window; streaks use GitHub calendar dates and are bounded by that window. PR counts cover public authored PRs, all time; stars cover owned public repositories. Optional commit-contribution and repository counts require a successful GitHub GraphQL response. No complete lifetime commit total is claimed.</sub>

[Contribution history](https://github.com/RahimovShaxriyor?tab=overview) &nbsp; · &nbsp; [Pull requests](https://github.com/search?q=author%3ARahimovShaxriyor+is%3Apr&type=pullrequests) &nbsp; · &nbsp; [Snapshot & definitions](assets/engineering/snapshot.json)

### Engineering Practices

- **Consistency & event delivery:** [row-level allocation locking](https://github.com/RahimovShaxriyor/hotelos-microservices/blob/main/reception-service/src/main/java/com/hotelos/reception/persistence/repository/RoomRepository.java) and [outbox publisher confirms / retry backoff](https://github.com/RahimovShaxriyor/hotelos-microservices/blob/main/reception-service/src/main/java/com/hotelos/reception/outbox/ReceptionOutboxDispatcher.java).
- **Schema & API contracts:** [Flyway migrations](https://github.com/RahimovShaxriyor/hotelos-microservices/tree/main/reception-service/src/main/resources/db/migration) and an [OpenAPI response matrix](https://github.com/RahimovShaxriyor/hotelos-microservices/blob/main/docs/api/OPENAPI_RESPONSE_MATRIX.md).
- **Authentication:** [RS256 tokens, BCrypt credentials, and account lockout](https://github.com/RahimovShaxriyor/hotelos-microservices/blob/main/docs/auth.md).
- **Reproducible environments:** [CloudWare Docker Compose topology](https://github.com/RahimovShaxriyor/cloudeware-pro/blob/main/docker-compose.yml) and [domain-service architecture](https://github.com/RahimovShaxriyor/cloudeware-pro/blob/main/docs/ARCHITECTURE.md).

### Featured repository activity

<!-- BEGIN VERIFIED PROJECT ACTIVITY -->
<sub>Source activity checked 2026-10-22 (UTC). File-filtered history; empty commits are excluded.</sub>

- **HotelOS** · [8eeba47](https://github.com/RahimovShaxriyor/hotelos-microservices/commit/8eeba47ef85e8b94e8bc354c318ced6bae6a7b21) · 2026-10-20 · feat(rooms): add room administration lifecycle and safe state repair (reception source).
  GitHub Actions: no workflows present.
- **CloudWare Pro** · [34ce7f1](https://github.com/RahimovShaxriyor/cloudeware-pro/commit/34ce7f12889ded05530cd00160ce6b5bf61ba1f6) · 2026-06-10 · update log in (backend + frontend).
  GitHub Actions: no workflows present.
- **Redis Visual Demo** · [a636388](https://github.com/RahimovShaxriyor/ExampleWeb-Redis/commit/a6363881ff6635c136a3e181732735db4fd6eb82) · 2026-05-19 · 1 (application source).
  GitHub Actions: no workflows present.
<!-- END VERIFIED PROJECT ACTIVITY -->

<details>
<summary>Scope &amp; update policy</summary>

The SVG and JSON are versioned snapshots from GitHub's public contribution calendar and APIs. The optional daily workflow refreshes actual data only; a failed collection retains the last successful snapshot and its date. No third-party statistics service is required.

The calendar can include empty or backdated commits recognized by GitHub. Source activity above is filtered to the named application paths and verified to contain changed files; it is not a claim about every change in each repository. Commit timestamps are not independent evidence of when work was performed.

No automated test suite or GitHub Actions pipeline was verified in the three featured repositories at the initial audit. Manual HTTP scenarios, dependency declarations, and container configuration are not presented as passing CI or test coverage. No code-review claim is made without review evidence.

</details>

<br>

## Engineering toolkit

<picture>
  <source media="(max-width: 640px)" srcset="assets/sr-toolkit-mobile.svg">
  <img src="assets/sr-toolkit.svg" width="100%" alt="Backend: Java, Spring Boot, Hibernate. Data and messaging: PostgreSQL, Redis, RabbitMQ. Frontend: React, TypeScript, Tailwind CSS. Infrastructure: Docker, Git, Linux, Nginx. AI and vision: Python, FastAPI, OpenCV.">
</picture>

<details>
<summary><b>Technologies &amp; working areas</b></summary>

- **Backend Engineering:** Java, Spring Boot, Spring Security, Hibernate, REST APIs.
- **Database &amp; Messaging:** PostgreSQL, Redis, RabbitMQ.
- **Frontend Development:** React, TypeScript, Vite, Tailwind CSS.
- **DevOps &amp; Infrastructure:** Docker, Git, Linux, Nginx, GitHub Actions / CI/CD.
- **AI / Computer Vision:** Python, FastAPI, MediaPipe, OpenCV.
- **Also working with:** Telegram Mini Apps.

</details>

<br>

## Currently building

**BTS · Full-Stack Software Engineer**  
February 2026 — Present

Java &amp; Spring Boot · React &amp; TypeScript · PostgreSQL · Docker

[Browse all repositories ↗](https://github.com/RahimovShaxriyor?tab=repositories) &nbsp; · &nbsp; [Contribution history](https://github.com/RahimovShaxriyor?tab=overview)

<br>

---

### Let’s connect.

For project inquiries and engineering conversations.

[**Email ↗**](mailto:rahimov55shah@gmail.com) &nbsp; · &nbsp; [**Telegram ↗**](https://t.me/raximovshaxriyor) &nbsp; · &nbsp; [**GitHub ↗**](https://github.com/RahimovShaxriyor)

<sub>Shaxriyor Rakhimov · APIs, events, and the systems that connect them.</sub>

