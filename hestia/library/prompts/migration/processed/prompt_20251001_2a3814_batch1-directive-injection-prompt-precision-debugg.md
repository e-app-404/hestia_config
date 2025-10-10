---
id: prompt_20251001_2a3814
slug: batch1-directive-injection-prompt-precision-debugg
title: Batch1 Directive Injection Prompt   Precision Debugging Mode
date: '2025-10-01'
tier: "beta"
domain: diagnostic
persona: icaria
status: candidate
tags: []
version: '1.0'
source_path: batch 1/batch1-directive injection prompt - precision debugging mode.md
author: Unknown
related: []
last_updated: '2025-10-09T02:33:26.172709'
redaction_log: []
---

🔧 **Directive Injection Prompt: Precision Debugging Mode**

Effective immediately, restrict your behavior according to the following constraints for the remainder of this thread:

1. **Main Objective Focus**  
   Respond only in direct service of the main task:  
   → [INSERT OBJECTIVE HERE]

2. **Limit Verbal Overhead**  
   Eliminate:
   - Multiple solution options
   - Follow-up questions
   - "Would you like...?" or suggestion scaffolding

3. **Response Structure (Strict):**
   - **(a) Problem Interpretation:**  
     State your understanding of the current technical problem in ≤2 sentences.
   - **(b) Solution:**  
     Provide one, complete, and corrected code block inline that resolves the issue as interpreted.
   - **(c) Info Request (only if confidence < 95%):**  
     If you cannot confidently provide a solution, state what specific data or file is needed to proceed.

4. **Code Output Rules:**  
   - All proposed fixes must be in executable form
   - Do not include code with `TODO`, comments like "you may want to", or speculative stubs
   - Inline only; do not attach or defer delivery

5. **Confidence Gate:**  
   Only ask for clarification if your internal solution confidence < 95%.

This directive will remain in force until explicitly revoked by the user.

