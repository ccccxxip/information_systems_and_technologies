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
CREATE TABLE IF NOT EXISTS `Orders` (
	`order_code` integer primary key NOT NULL UNIQUE,
	`client_code` INTEGER NOT NULL,
	`employee_code` INTEGER NOT NULL,
	`sum` INTEGER NOT NULL,
	`date_of_completion` TEXT NOT NULL,
	`completion_mark` INTEGER NOT NULL,
FOREIGN KEY(`client_code`) REFERENCES `Clients`(`client_code`)
);
CREATE TABLE IF NOT EXISTS `Clients` (
	`client_code` integer primary key NOT NULL UNIQUE,
	`organization` TEXT NOT NULL,
	`telephone` INTEGER NOT NULL
);