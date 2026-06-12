from __future__ import annotations
import argparse, json, sys, zipfile
from pathlib import Path
STAGE='1002F_TEACHER_CONTROL_AND_PUBLIC_DISPLAY_LOW_FIDELITY_PROTOTYPE'
FINAL='XIAOJIAO_TEACHER_CONTROL_AND_PUBLIC_DISPLAY_LOW_FIDELITY_PROTOTYPE_PASS'
SLUG='xiaojiao_teacher_control_and_public_display_low_fidelity_prototype_1002F'
MARKER='ALL_1002F_TEACHER_CONTROL_AND_PUBLIC_DISPLAY_LOW_FIDELITY_PROTOTYPE_CHECKS_OK'
SAMPLE='teacher_display_pair_fixture_1002F.json'
HTMLS=["teacher_control_surface.html","public_display_surface.html"]
BAD_PARTS=[".env","token","secret","key","node_modules","__pycache__",".db",".sqlite","dist","build","coverage",".DS_Store"]
def fail(m): raise SystemExit(f'VALIDATION_FAILED: {m}')
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root'); a=ap.parse_args(); root=Path(a.root).resolve() if a.root else Path(__file__).resolve().parents[1]
    req=['docs/audit/xiaojiao_1002A_1002B_progressive_surface_foundation_summary.json',f'docs/foundation/{SLUG}.md',f'docs/foundation/{SLUG}.json',f'samples/{SLUG}/{SAMPLE}',f'docs/audit/{SLUG}_result.json',f'docs/audit/{SLUG}_report.md',f'docs/audit_packages/{SLUG}_manifest.json',f'scripts/validate_{SLUG}.py']+[f'samples/{SLUG}/'+h for h in HTMLS]
    for r in req:
        if not (root/r).exists(): fail(f'missing required file: {r}')
    summary=load(root/'docs/audit/xiaojiao_1002A_1002B_progressive_surface_foundation_summary.json')
    if summary.get('overall_status')!='1002_PROGRESSIVE_SURFACE_FOUNDATION_BASELINE_ACCEPTED': fail('1002A-B summary gate mismatch')
    contract=load(root/f'docs/foundation/{SLUG}.json'); sample=load(root/f'samples/{SLUG}/{SAMPLE}'); result=load(root/f'docs/audit/{SLUG}_result.json'); manifest=load(root/f'docs/audit_packages/{SLUG}_manifest.json')
    if contract.get('stage_code')!=STAGE or sample.get('stage_code')!=STAGE or result.get('stage_code')!=STAGE: fail('stage identity mismatch')
    if result.get('final_status')!=FINAL or result.get('pass') is not True or result.get('marker')!=MARKER: fail('result mismatch')
    for mapping in [contract.get('hard_boundaries',{}), sample.get('boundary_flags',{}), result.get('boundary_flags',{})]:
        for k,v in mapping.items():
            if v is not False: fail(f'unsafe boundary {k}')
    if STAGE.startswith('1002C'):
        if set(sample.get('surface_modes',[]))!={'light_entry','focus_surface','grid_studio','analysis_board'}: fail('surface mode coverage mismatch')
    elif STAGE.startswith('1002D'):
        for key in ['surface_mode_schema','zone_type_schema','card_type_schema','layout_schema','layout_memory_policy','card_allowed_zone_rules','business_pack_layout_presets']:
            if key not in sample: fail(f'missing {key}')
        if len(sample.get('business_pack_layout_presets',[])) < 6: fail('business pack presets too few')
    elif STAGE.startswith('1002E'):
        for key in ['teaching_scene_bundle','teacher_control_surface','public_display_surface','classroom_tool_cards','classroom_resource_cards','principles']:
            if key not in sample: fail(f'missing {key}')
        if sample['principles'].get('ppt_is_not_product_model') is not True or sample['principles'].get('no_real_display_runtime') is not True: fail('classroom principles mismatch')
    elif STAGE.startswith('1002F'):
        if sample.get('sample_lesson')!='四年级美术《色彩的感觉》': fail('sample lesson mismatch')
        rules=sample.get('separation_rules',{})
        for k in ['teacher_only_info_on_teacher_surface','public_display_student_facing_only','no_ipc','no_websocket','no_display_runtime','no_student_runtime','no_classroom_sync']:
            if rules.get(k) is not True: fail(f'missing separation rule {k}')
    elif STAGE.startswith('1002G'):
        if set(sample.get('zones',[]))!={'student_work_gallery_zone','evaluation_dimension_zone','class_distribution_zone','typical_cases_zone','ai_candidate_comment_zone','teacher_review_zone'}: fail('analysis board zones mismatch')
        rules=sample.get('rules',{})
        for k in ['ai_comment_candidate_only','teacher_review_required','no_formal_scoring','no_formal_export','no_student_data_runtime','no_database_write']:
            if rules.get(k) is not True: fail(f'missing rule {k}')
    elif STAGE.startswith('1002H'):
        for key in ['surface_mode_decision_matrix','business_pack_to_surface_mapping','dependency_install_decision_gate','ui_prototype_caveat','next_stage_options']:
            if key not in sample: fail(f'missing {key}')
        if sample['dependency_install_decision_gate'].get('current_dependency_install') is not False or sample['dependency_install_decision_gate'].get('user_confirmation_required') is not True: fail('dependency gate mismatch')
    z=root/f'docs/audit_packages/{SLUG}.zip'
    if not z.exists(): fail('missing zip')
    with zipfile.ZipFile(z) as zf: entries=zf.namelist()
    for e in entries:
        n=e.replace('\\','/')
        if n.startswith('/') or ':' in n or '\\' in e: fail(f'unsafe zip path {e}')
        if any(part.lower() in n.lower() for part in BAD_PARTS): fail(f'forbidden zip entry {e}')
    if manifest.get('manifest_minus_zip')!=[] or manifest.get('zip_minus_manifest')!=[] or sorted(manifest.get('zip_entries',[]))!=sorted(entries): fail('manifest zip mismatch')
    print(MARKER); return 0
if __name__=='__main__': sys.exit(main())