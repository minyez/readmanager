# Reading Manager

## Motivation

This is a simple manager for the personal reading, especially for books and note-taking.

DouBan only provides the way to mark the book you are reading or have read, 
but have no way to take care where you have been reading at present.
I have **always** been forgeting the books I am reading, as so many stuffs disturbing.
This is why I launch this project.

## Usage

Add `readmanager` to `PATH`, run
```bash
$ readmana
```
in terminal. For help information, run
```bash
$ readmana -h
```

## Configuration

`readmana` use a json file for configuration, default `~/.config/readmana/config.json`.
If it is not found and the environment variable `READMANA_CONFIG` is not set, 
`readmana` will interactively generate the default configuration file.
 To use custom path, you need to specify a valide `READMANA_CONFIG`.
