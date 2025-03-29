CREATE TABLE [job_titles] (
	[id_job_title] int IDENTITY(1,1) NOT NULL UNIQUE,
	[name] nvarchar(max) NOT NULL,
	PRIMARY KEY ([id_job_title])
);

CREATE TABLE [employees] (
	[id] int IDENTITY(1,1) NOT NULL UNIQUE,
	[surname] nvarchar(max) NOT NULL,
	[name] nvarchar(max) NOT NULL,
	[id_job_title] int NOT NULL,
	PRIMARY KEY ([id])
);


ALTER TABLE [employees] ADD CONSTRAINT [employees_fk3] FOREIGN KEY ([id_job_title]) REFERENCES [job_titles]([id_job_title]);