# WAF Evaluation Results — V3 Checkpoints

> Date: 2026-05-12  
> WAF: ModSecurity OWASP CRS (Docker, port 8080, healthy)  
> Samples: 500 per checkpoint (pre-generated từ V3 checkpoints)

---

## Kết quả So Sánh: No-WAF vs With-WAF

| Checkpoint | No-WAF Composite | WAF Composite | OWASP bypass | DB% | AST-H | IDS% | Uniq |
|---|---|---|---|---|---|---|---|
| V3 step1000 | 0.460 | **0.491** | **9.8%** | 99.8% | 2.911 | 2.2% | 0.926 |
| **V3 step2000 ★** | **0.471** | 0.476 | 2.0% | 99.0% | 3.065 | 0.0% | **1.000** |
| V3 step12000 (collapsed) | 0.357 | 0.488 | 43.4% | 100% | 2.666 | 0.0% | 0.008 |
| V3 final (collapsed) | 0.357 | 0.468 | 36.8% | 100% | 2.661 | 0.0% | 0.008 |

**Kết luận quan trọng**: Thứ hạng thay đổi khi bật WAF.

---

## Phân Tích

### Nghịch lý collapsed model vs WAF

Model collapsed (step12000, step final) tạo ra 1-2 payload đơn giản như `1 or 'root'` và `- -1 and 'root'`. Những payload này có **OWASP bypass cao (43%)** vì:

- WAF OWASP CRS thiết kế để chặn các pattern injection phức tạp
- Payload quá đơn giản → không match signature CRS phức tạp
- Nhưng diversity **cực thấp** (uniqueness=0.008) → không có giá trị thực tế

### Step1000 vs Step2000 với WAF

| Metric | Step1000 | Step2000 |
|---|---|---|
| **WAF Composite** | **0.491** | 0.476 |
| OWASP bypass | **9.8%** | 2.0% |
| Re-lex uniqueness | 0.926 | **1.000** |
| AST entropy | 2.911 | **3.065** |

Step1000 tốt hơn với WAF vì nó vừa có diversity cao vừa bypass được WAF ở mức hợp lý.

### Khuyến nghị tùy use-case

| Use-case | Best checkpoint |
|---|---|
| **Diversity tối đa** (red-team dataset) | `v3/adv_step2000.pt` |
| **WAF bypass + diversity** (pentest simulation) | `v3/adv_step1000.pt` |
| **Tối đa OWASP bypass** (WAF stress test) | `v3/adv_step12000.pt` ⚠️ diversity thấp |

---

## Composite Score Formula (nhắc lại)

```
composite = 0.30 * owasp_bypass
          + 0.25 * db_exec
          + 0.20 * (ast_entropy / 5.0)
          + 0.15 * ids_evasion
          + 0.10 * relex_uniqueness
```

---

## Files Kết Quả

| File | Mô tả |
|---|---|
| `eval/results_v3/v3_adv_step1000_waf.json` | WAF eval step1000 |
| `eval/results_v3/v3_adv_step2000_waf.json` | WAF eval step2000 (best no-WAF) |
| `eval/results_v3/v3_adv_step12000_waf.json` | WAF eval step12000 (collapsed) |
| `eval/results_v3/v3_adv_final_waf.json` | WAF eval final (collapsed) |
| `eval/results_v3/v3_adv_step*.json` | No-WAF eval (baseline) |
