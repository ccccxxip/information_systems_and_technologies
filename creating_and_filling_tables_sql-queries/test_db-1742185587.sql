CREATE TABLE IF NOT EXISTS `job_titles` (
	`id_job_title` integer primary key NOT NULL UNIQUE,
	`name` TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS `employees` (
	`id` integer primary key NOT NULL UNIQUE,
	`surname` TEXT NOT NULL,
	`name` TEXT NOT NULL,
	`id_job_title` INTEGER NOT NULL,
FOREIGN KEY(`id_job_title`) REFERENCES `job_titles`(`id_job_title`)
);