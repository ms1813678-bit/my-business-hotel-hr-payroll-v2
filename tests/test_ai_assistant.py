from app.ai_assistant import build_system_prompt, local_fallback_answer


def test_ai_system_prompt_is_advisory():
    prompt = build_system_prompt()
    assert "مساعد موارد بشرية محلي" in prompt
    assert "مراجعة وتأكيد" in prompt


def test_ai_fallback_reads_dashboard_metrics():
    answer = local_fallback_answer(
        "كم عدد الموظفين النشطين؟",
        {"metrics": {"active_employees": 7}},
    )
    assert answer == "عدد الموظفين النشطين حاليًا: 7."


def test_ai_fallback_keeps_core_system_usable_when_model_is_unavailable():
    answer = local_fallback_answer(
        "ساعدني في شيء آخر",
        {"metrics": {}},
    )
    assert "غير متاح حاليًا" in answer


def test_ai_command_requires_explicit_execute_prefix():
    from app.ai_agent import is_command_request, wants_execution
    assert is_command_request("اعتمد مسير الرواتب رقم 1")
    assert not wants_execution("اعتمد مسير الرواتب رقم 1")
    assert wants_execution("نفذ: اعتمد مسير الرواتب رقم 1")


def test_ai_command_allowlist_does_not_include_arbitrary_operations():
    from app.ai_agent import ALLOWED_ACTIONS
    assert "approve_payroll_run" in ALLOWED_ACTIONS
    assert "run_sql" not in ALLOWED_ACTIONS
    assert "shell" not in ALLOWED_ACTIONS


def test_employee_management_actions_are_allowlisted():
    from app.ai_agent import ALLOWED_ACTIONS
    for action in ("create_employee", "edit_employee", "transfer_employee", "archive_employee", "rehire_employee"):
        assert action in ALLOWED_ACTIONS


def test_ai_network_policy_accepts_only_loopback():
    from app.ai_agent import _loopback_only
    assert _loopback_only("http://127.0.0.1:11434")
    assert _loopback_only("http://localhost:11434")
    assert not _loopback_only("https://example.com:11434")


def test_ai_command_supports_manual_attendance_and_safe_draft_leave_deletion():
    from app.ai_agent import ALLOWED_ACTIONS, is_command_request

    assert "create_manual_attendance" in ALLOWED_ACTIONS
    assert "delete_draft_leave" in ALLOWED_ACTIONS
    assert is_command_request("سجل حضور يدوي للموظف MY-0001")
    assert is_command_request("احذف مسودة الإجازة رقم 12")


def test_run_ai_command_never_executes_even_with_explicit_execute_prefix(monkeypatch):
    import app.ai_agent as agent
    import app.ai_gateway as gateway
    from datetime import datetime, timezone

    called = {}
    def fake_prepare(question, actor):
        called["actor"] = actor
        return {
            "token": "one-time-token",
            "plan": {"action": "approve_payroll_run", "payroll_run_id": 9},
            "summary": "اعتماد مسير الرواتب رقم 9",
            "expires_at": datetime(2026, 11, 20, tzinfo=timezone.utc),
        }

    def forbidden_execute(*args, **kwargs):
        raise AssertionError("run_ai_command must never execute a write")

    monkeypatch.setattr(gateway, "prepare_command", fake_prepare)
    monkeypatch.setattr(agent, "execute_plan", forbidden_execute)
    result = agent.run_ai_command("نفذ: اعتمد مسير الرواتب رقم 9", "hr-admin")

    assert result["executed"] is False
    assert result["pending"] is True
    assert result["token"] == "one-time-token"
    assert called["actor"] == "hr-admin"
