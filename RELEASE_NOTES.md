# Application Release Notes

## v0.4.0 (2018-08-07)
* Added ability to render multiple templates at once. This change deprecates
the template and dest positional arguments and introduces a new named argument
called --template.
* Bug fix to no pre-render the templates when the app starts if there's an
issue when connecting to Rancher.)

## v0.3.0 (2017-01-18)
* Added ability to listen for changes to multiple services under the same stack.

## v0.2.1 (2016-10-07)
* Bug fix to ignore messages from instances that don't have labels (e.g Network
Agent)

## v0.2.0 (2016-10-07)
* Added ability to pre-render the template even it no stack and/or service are
specified.
* Added the ability to load all environment instances when a message from the
web socket is received and no filters are specified.

## v0.1.2 (2016-09-09)
* Additional changes for open source release.

## v0.1.1 (2016-09-09)
* Python 3 compatibility.

## v0.1.0 (2016-09-08)
* Initial release. Includes:
  * Logic to listen for changes in Rancher.
  * Logic to render a template after a change has been captured.
  * Logic to run a notification command after the template has been rendered.
