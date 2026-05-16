# -*- coding: utf-8 -*-
"""Shared field definitions for CVE description completeness analysis."""

FIELD_CN = {
    "has_specific_vuln_type": "具体漏洞类型",
    "has_big_category": "大类漏洞",
    "has_core_feature": "核心特征",
    "has_trigger_condition": "触发条件",
    "has_specific_error_point": "具体错误点",
    "has_error_type_attribution": "错误类型归属",
    "has_direct_program_anomaly": "直接程序异常",
    "has_vendor_or_maintainer": "产品开发主体",
    "has_product_name": "产品名称",
    "has_affected_version": "受影响版本",
    "has_affected_component": "受影响组件",
    "has_environment_constraint": "影响环境",
    "has_attacker_identity_type": "攻击者身份类型",
    "has_attacker_privilege_traits": "攻击者权限特征",
    "has_attack_operation_method": "攻击操作方式",
    "has_precondition_constraints": "前置约束条件",
    "has_core_impact_type": "核心影响类型",
    "has_specific_harm_action": "具体危害行为",
    "has_harm_constraints": "危害约束条件",
    "has_followon_escalation_harm": "后续衍生危害",
    "has_vector_general_class": "载体大类",
    "has_vector_specific_form": "载体具体形态",
    "has_vector_delivery_method": "载体传递方式",
    "has_specific_attack_point": "具体受攻击点",
}

FIELD_GROUPS = {
    "漏洞类型": [
        "has_specific_vuln_type", "has_big_category", "has_core_feature", "has_trigger_condition"
    ],
    "根本原因": [
        "has_specific_error_point", "has_error_type_attribution", "has_direct_program_anomaly"
    ],
    "受影响产品": [
        "has_vendor_or_maintainer", "has_product_name", "has_affected_version",
        "has_affected_component", "has_environment_constraint"
    ],
    "攻击者类型": [
        "has_attacker_identity_type", "has_attacker_privilege_traits",
        "has_attack_operation_method", "has_precondition_constraints"
    ],
    "影响": [
        "has_core_impact_type", "has_specific_harm_action",
        "has_harm_constraints", "has_followon_escalation_harm"
    ],
    "攻击载体": [
        "has_vector_general_class", "has_vector_specific_form",
        "has_vector_delivery_method", "has_specific_attack_point"
    ],
}

FIELD_CATEGORY = {
    field: category
    for category, fields in FIELD_GROUPS.items()
    for field in fields
}

FIELD_ORDER = [field for fields in FIELD_GROUPS.values() for field in fields]
