"""Streamlit GUI orchestration for STSMODDER."""
from __future__ import annotations

import logging
from typing import Dict

import streamlit as st

from jpypetestorchestrator import ORCHESTRATOR, JPypeTestOrchestrator
from logic import APPLICATION_LOGIC, ApplicationLogic
from plugin_manager import PluginManager


class StreamlitGUI:
    """Coordinates Streamlit rendering and user interaction."""

    def __init__(
        self,
        logic: ApplicationLogic,
        orchestrator: JPypeTestOrchestrator,
        plugin_manager: PluginManager,
    ) -> None:
        self._logic = logic
        self._orchestrator = orchestrator
        self._plugin_manager = plugin_manager
        self._logger = logging.getLogger("stsm.streamlit_gui")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        self._logger.setLevel(logging.INFO)
        self._plugin_manager.register_module(__name__, __import__(__name__))
        self._plugin_manager.register_symbol("gui.streamlit_gui", self)

    def render(self) -> None:
        st.set_page_config(page_title="STSMODDER", layout="wide")
        self._ensure_session_state()
        self._render_dependency_modal()
        self._render_sidebar()
        self._render_main_sections()

    def _ensure_session_state(self) -> None:
        config = self._logic.runtime_config
        defaults = {
            "java_home": config.java_home,
            "modthespire_jar": config.modthespire_jar,
            "basemod_path": config.basemod_path,
            "stslib_path": config.stslib_path,
            "actlikeit_path": config.actlikeit_path,
            "suppress_dependency_modal": config.suppress_dependency_modal,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        if "last_test_results" not in st.session_state:
            st.session_state["last_test_results"] = None

    def _render_dependency_modal(self) -> None:
        if st.session_state.get("suppress_dependency_modal", False):
            return
        if not st.session_state.get("dependency_modal_css", False):
            st.markdown(
                """
                <style>
                .dependency-modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.6);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 9999;
                }
                .dependency-modal-content {
                    background-color: var(--background-color, #ffffff);
                    color: inherit;
                    padding: 1.75rem;
                    border-radius: 0.75rem;
                    max-width: 720px;
                    max-height: 70vh;
                    overflow-y: auto;
                    box-shadow: 0 0 18px rgba(0, 0, 0, 0.35);
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            st.session_state["dependency_modal_css"] = True
        placeholder = st.empty()
        with placeholder.container():
            st.markdown(
                "<div class='dependency-modal-overlay'><div class='dependency-modal-content'>",
                unsafe_allow_html=True,
            )
            st.markdown("### Modding Library Requirements")
            st.markdown(
                """
                **BaseMod requires Java 8 and ModTheSpire v3.1.0+**. Ensure the `desktop-1.0.jar` from
                your Slay the Spire installation is available. StSLib builds on BaseMod, and ActLikeIt extends
                the dungeon/act system. Configure their jar paths below before launching tests or exports.
                """
            )
            suppress = st.checkbox(
                "Do not show again",
                value=st.session_state.get("suppress_dependency_modal", False),
                key="dependency_modal_checkbox",
            )
            close_clicked = st.button("Close requirements", key="dependency_modal_close")
            st.markdown("</div></div>", unsafe_allow_html=True)
        if close_clicked:
            st.session_state["suppress_dependency_modal"] = suppress
            self._logic.update_configuration(suppress_dependency_modal=suppress)
            placeholder.empty()
            st.rerun()

    def _render_sidebar(self) -> None:
        with st.sidebar:
            st.header("Runtime Configuration")
            with st.form("configuration_form"):
                java_home = st.text_input("Java Home", st.session_state.get("java_home", ""))
                modthespire_jar = st.text_input("ModTheSpire Jar", st.session_state.get("modthespire_jar", ""))
                basemod_path = st.text_input("BaseMod Jar", st.session_state.get("basemod_path", ""))
                stslib_path = st.text_input("StSLib Jar", st.session_state.get("stslib_path", ""))
                actlikeit_path = st.text_input("ActLikeIt Jar", st.session_state.get("actlikeit_path", ""))
                submitted = st.form_submit_button("Save Configuration")
            if submitted:
                self._update_config(
                    java_home=java_home,
                    modthespire_jar=modthespire_jar,
                    basemod_path=basemod_path,
                    stslib_path=stslib_path,
                    actlikeit_path=actlikeit_path,
                )
                st.success("Configuration saved successfully")
            self._render_environment_status()

    def _render_environment_status(self) -> None:
        validation = self._logic.validate_environment()
        st.subheader("Environment Status")
        for key, is_valid in validation.items():
            label = key.replace("_", " ").title()
            if is_valid:
                st.success(f"{label}: OK")
            else:
                st.warning(f"{label}: Missing or invalid")

    def _render_main_sections(self) -> None:
        tabs = st.tabs(["JPype Bridge", "Libraries", "Plugins", "Tests"])
        self._render_bridge_tab(tabs[0])
        self._render_library_tab(tabs[1])
        self._render_plugin_tab(tabs[2])
        self._render_tests_tab(tabs[3])

    def _render_bridge_tab(self, container: st.delta_generator.DeltaGenerator) -> None:
        with container:
            state = self._logic.bridge_controller.get_state()
            st.metric("JVM State", state.value)
            cols = st.columns(2)
            if cols[0].button("Start JVM", use_container_width=True):
                try:
                    self._logic.bridge_controller.start_jvm()
                    st.toast("JVM started successfully", icon="✅")
                except Exception as exc:  # pylint: disable=broad-except
                    st.toast(f"Failed to start JVM: {exc}", icon="❌")
            if cols[1].button("Shutdown JVM", use_container_width=True):
                try:
                    self._logic.bridge_controller.shutdown_jvm()
                    st.toast("JVM shutdown complete", icon="✅")
                except Exception as exc:  # pylint: disable=broad-except
                    st.toast(f"Failed to shutdown JVM: {exc}", icon="❌")

    def _render_library_tab(self, container: st.delta_generator.DeltaGenerator) -> None:
        with container:
            st.subheader("Configured Libraries")
            config = self._logic.runtime_config
            st.json(
                {
                    "java_home": config.java_home,
                    "modthespire": config.modthespire_jar,
                    "basemod": config.basemod_path,
                    "stslib": config.stslib_path,
                    "actlikeit": config.actlikeit_path,
                    "enabled_libraries": config.enabled_libraries,
                }
            )

    def _render_plugin_tab(self, container: st.delta_generator.DeltaGenerator) -> None:
        with container:
            st.subheader("Plugin Registry")
            registry = self._plugin_manager.export_registry()
            st.json(registry)
            loaded = list(self._plugin_manager.get_loaded_plugins())
            st.write("Loaded Plugins", loaded)

    def _render_tests_tab(self, container: st.delta_generator.DeltaGenerator) -> None:
        with container:
            st.subheader("Integration Test Suites")
            suites = self._orchestrator.get_suites()
            if not suites:
                st.info("No test suites are currently registered")
                return
            selected = st.selectbox("Select a suite", suites)
            if st.button("Run Suite", key="run_suite"):
                try:
                    results = self._orchestrator.execute_suite(selected)
                    st.session_state["last_test_results"] = results
                    st.toast("Test suite execution completed", icon="✅")
                except Exception as exc:  # pylint: disable=broad-except
                    st.session_state["last_test_results"] = {"error": str(exc)}
                    st.toast(f"Test suite failed: {exc}", icon="❌")
            last_results = st.session_state.get("last_test_results")
            if last_results:
                st.subheader("Last Results")
                st.json(last_results)

    def _update_config(self, **values: str) -> None:
        sanitized: Dict[str, str] = {}
        for key, value in values.items():
            sanitized[key] = value.strip()
            st.session_state[key] = sanitized[key]
        self._logic.update_configuration(**sanitized)


if __name__ == "__main__":
    gui = StreamlitGUI(APPLICATION_LOGIC, ORCHESTRATOR, PluginManager.get_instance())
    gui.render()
