---
description: 'Verify checkpoint completion and prepare for next'
---

# Checkpoint Completion Protocol

When you believe a checkpoint is complete:

1. **Review Success Criteria**
   - Read the checkpoint file
   - Verify EACH criterion is met
   - Provide evidence for each

2. **Run Verification**
   - Execute any test commands specified
   - Capture output as proof

3. **Update Documentation**
   - Mark checkboxes in checkpoint file
   - Update STATUS.md with completion

4. **Commit Changes**
   - Stage all modified files
   - Use commit message: `feat(phase-X): complete checkpoint X.Y - [description]`
   - Push to repository

5. **Prepare for Audit**
   - Invoke the Auditor agent if available
   - Or manually verify against gate criteria

6. **Next Checkpoint**
   - Only proceed after audit passes
   - Load the next checkpoint file
   - Do NOT carry over context from previous checkpoint
