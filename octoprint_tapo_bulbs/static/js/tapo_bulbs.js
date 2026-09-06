/* Tapo Bulbs - OctoPrint plugin frontend. */
$(function () {
    "use strict";

    var PLUGIN_ID = "tapo_bulbs";

    function TapoBulbsViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];
        self.loginState = parameters[1];
        self.access = parameters[2];

        self.states = ko.observable({});
        self.configured = ko.observableArray([]);
        self.connectionError = ko.observable(null);
        self.bulbs = ko.observableArray([]);
        self.discoveredLights = ko.observableArray([]);
        self.testing = ko.observable(false);
        self.loadingLights = ko.observable(false);
        self.testResult = ko.observable("");
        self.testOk = ko.observable(true);
        self.pluginSettings = null;

        self.canControl = ko.pureComputed(function () {
            return self.loginState.hasPermission(
                self.access.permissions.PLUGIN_TAPO_BULBS_CONTROL
            );
        });

        self.testResultClass = ko.pureComputed(function () {
            return self.testOk() ? "text-success" : "text-error";
        });

        self.navbarBulbs = ko.pureComputed(function () {
            var states = self.states();
            return self.configured().filter(function (bulb) {
                return bulb.show_in_navbar !== false;
            }).map(function (bulb) {
                var state = states[bulb.entity_id] || {};
                return {
                    entity_id: bulb.entity_id,
                    label: bulb.label || bulb.entity_id,
                    state: state.state || "unknown",
                    stateClass: "tapo-bulbs-state-" + (state.state || "unknown"),
                    brightnessText: state.brightness === null || state.brightness === undefined
                        ? ""
                        : Math.round(state.brightness / 255 * 100) + "%"
                };
            });
        });

        function command(name, payload) {
            return OctoPrint.simpleApiCommand(PLUGIN_ID, name, payload || {});
        }

        function applyPayload(payload) {
            if (!payload) return;
            if (payload.bulbs !== undefined) self.configured(payload.bulbs);
            if (payload.states !== undefined) self.states(payload.states);
            if (payload.error !== undefined) self.connectionError(payload.error);
        }

        function reportFailure(response) {
            new PNotify({
                title: "Tapo Bulbs",
                text: (response && response.error) || "Request failed.",
                type: "error"
            });
        }

        self.refresh = function () {
            OctoPrint.simpleApiGet(PLUGIN_ID).done(applyPayload);
        };

        self.turnOn = function (bulb) {
            command("turn_on", {entity_id: bulb.entity_id}).done(function (response) {
                if (response && response.ok === false) reportFailure(response);
            });
        };

        self.turnOff = function (bulb) {
            command("turn_off", {entity_id: bulb.entity_id}).done(function (response) {
                if (response && response.ok === false) reportFailure(response);
            });
        };

        function settingsModel() {
            return self.pluginSettings || self.settings.settings.plugins[PLUGIN_ID];
        }

        function makeRow(source) {
            source = source || {};
            return {
                entity_id: ko.observable(source.entity_id || ""),
                label: ko.observable(source.label || ""),
                show_in_navbar: ko.observable(source.show_in_navbar !== false),
                on_print_start: ko.observable(source.on_print_start !== false),
                off_print_done: ko.observable(source.off_print_done !== false),
                off_print_failed: ko.observable(source.off_print_failed !== false),
                off_print_cancelled: ko.observable(source.off_print_cancelled !== false),
                brightness_pct: ko.observable(source.brightness_pct || ""),
                color_temp_kelvin: ko.observable(source.color_temp_kelvin || "")
            };
        }

        function connectionPayload() {
            var settings = settingsModel();
            return {
                base_url: settings.base_url(),
                access_token: settings.access_token(),
                verify_certificate: settings.verify_certificate()
            };
        }

        self.addBulb = function () {
            self.bulbs.push(makeRow());
        };

        self.removeBulb = function (row) {
            self.bulbs.remove(row);
        };

        self.loadBulbRows = function () {
            var stored = ko.toJS(settingsModel().bulbs) || [];
            self.bulbs(stored.map(makeRow));
        };

        self.testConnection = function () {
            self.testing(true);
            self.testResult("Testing...");
            command("test_connection", connectionPayload()).done(function (response) {
                self.testOk(!!(response && response.ok));
                self.testResult(response && response.ok
                    ? "Connected to Home Assistant."
                    : (response && response.error) || "Connection failed.");
            }).fail(function () {
                self.testOk(false);
                self.testResult("Connection failed.");
            }).always(function () {
                self.testing(false);
            });
        };

        self.loadLights = function () {
            self.loadingLights(true);
            command("list_lights", connectionPayload()).done(function (response) {
                if (!response || response.ok === false) {
                    reportFailure(response);
                    return;
                }
                self.discoveredLights(response.lights || []);
            }).always(function () {
                self.loadingLights(false);
            });
        };

        self.onBeforeBinding = function () {
            self.pluginSettings = self.settings.settings.plugins[PLUGIN_ID];
            self.loadBulbRows();
        };

        self.onSettingsShown = function () {
            self.loadBulbRows();
            self.testResult("");
        };

        self.onSettingsBeforeSave = function () {
            var rows = self.bulbs().map(function (row) {
                return {
                    entity_id: (row.entity_id() || "").trim(),
                    label: (row.label() || "").trim(),
                    show_in_navbar: row.show_in_navbar(),
                    on_print_start: row.on_print_start(),
                    off_print_done: row.off_print_done(),
                    off_print_failed: row.off_print_failed(),
                    off_print_cancelled: row.off_print_cancelled(),
                    brightness_pct: row.brightness_pct(),
                    color_temp_kelvin: row.color_temp_kelvin()
                };
            }).filter(function (row) {
                return row.entity_id.indexOf("light.") === 0;
            });
            settingsModel().bulbs(rows);
        };

        self.onDataUpdaterPluginMessage = function (plugin, message) {
            if (plugin !== PLUGIN_ID || !message) return;
            if (message.type === "states") {
                applyPayload(message);
            } else if (message.type === "automation" && message.state === "failed") {
                var failures = message.failures || [];
                reportFailure({
                    error: failures.length
                        ? failures.map(function (item) {
                            return item.entity_id + ": " + item.error;
                        }).join("; ")
                        : "The automatic light action failed."
                });
            }
        };

        self.onAfterBinding = function () {
            self.refresh();
        };

        self.onUserPermissionsChanged = self.onUserLoggedIn = self.onUserLoggedOut = function () {
            self.refresh();
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: TapoBulbsViewModel,
        dependencies: ["settingsViewModel", "loginStateViewModel", "accessViewModel"],
        elements: ["#navbar_plugin_tapo_bulbs", "#settings_plugin_tapo_bulbs"]
    });
});
