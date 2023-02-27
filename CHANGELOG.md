# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- Template

## [0.0.1] - 1970-01-01
### Added

- X
- Y

### Changed
### Deprecated
### Removed
### Fixed
### Security
-->

## [Unreleased]

## [0.3.1] - 2023-02-27

### Fixed

- Fix `methodic_cache.cached_method` not working with classes that inherit from slotted classes (but that are not slotted themselves) https://github.com/youtux/methodic_cache/pull/5

## [0.3.0] - 2023-02-23

### Changed

- `methodic_cache.default_cache_factory` is now `methodic_cache.simple_cache_factory`

## [0.2.1] - 2023-02-21

### Fixed

- Update pyproject.toml with the correct URL for the repository and homepage.


## [0.2.0] - 2023-02-21

Initial public release
