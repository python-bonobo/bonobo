Contributing
============

Contributing to bonobo is simple. Although we don't have a complete guide on this topic for now, the best way is to fork
the github repository and send pull requests.

A few guidelines...

* Starting at 1.0, the system needs to be 100% backward compatible. Best way to do so is to ensure the actual expected
  behavior is unit tested before making any change. See http://semver.org/.
* There can be changes before 1.0, even backward incompatible changes. There should be a reason for a BC break, but
  I think it's best for the speed of development right now.
* The core should stay as light as possible.
* Coding standards are enforced using yapf. That means that you can code the way you want, we just ask you to run
  `make format` before committing your changes so everybody follows the same conventions.
* General rule for anything you're not sure about is "open a github issue to discuss the point".
* More formal proposal process will come the day we feel the need for it.

Issues: https://github.com/python-bonobo/bonobo/issues

Roadmap: https://www.bonobo-project.org/roadmap

Slack: https://bonobo-slack.herokuapp.com/
