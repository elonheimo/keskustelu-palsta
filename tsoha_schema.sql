CREATE TABLE "users" (
  "id" SERIAL PRIMARY KEY,
  "name" TEXT UNIQUE,
  "password" TEXT,
  "time" timestamp,
  "admin" boolean
);

CREATE TABLE "topics" (
  "id" SERIAL PRIMARY KEY,
  "title" TEXT UNIQUE,
  "time" timestamp,
  "secret" boolean
);

CREATE TABLE "posts" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER,
  "title" TEXT,
  "message" TEXT,
  "topic_id" INTEGER,
  "created" timestamp,
  "edited" timestamp
);

CREATE TABLE "messages" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER,
  "message" TEXT,
  "created" timestamp,
  "edited" timestamp,
  "post_id" INTEGER
);

CREATE TABLE "secret_access" (
  "topic_id" INTEGER,
  "user_id" INTEGER
);

ALTER TABLE "posts" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "posts" ADD FOREIGN KEY ("topic_id") REFERENCES "topics" ("id");

ALTER TABLE "messages" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "messages" ADD FOREIGN KEY ("post_id") REFERENCES "posts" ("id");

ALTER TABLE "secret_access" ADD FOREIGN KEY ("topic_id") REFERENCES "topics" ("id");

ALTER TABLE "secret_access" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");
