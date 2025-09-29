# REST API Planning

[todo] Expose a `/runtime/jvm` endpoint supporting `GET` for status, `POST` for start, and `DELETE` for shutdown, mapping directly to `logic.JPypeBridgeController` methods to mirror GUI controls.

[todo] Provide a `/runtime/plugins` endpoint delivering the plugin registry snapshot as returned by `plugin_manager.PluginManager.export_registry()` so automation environments can inspect available hooks.

[todo] Add a `/tests/run` endpoint that accepts a payload describing desired smoke/integration suites, invoking `jpypetestorchestrator.JPypeTestOrchestrator.execute_suite` and streaming structured results.

[todo] Integrate authentication and audit logging for all runtime-affecting endpoints to ensure parity with GUI actions and maintain traceability.
