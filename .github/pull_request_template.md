## Summary

- 

## Change Type

- [ ] Documentation
- [ ] Workflow example
- [ ] IAM or trust policy example
- [ ] Repository hygiene

## OIDC / AWS Safety Checklist

- [ ] No long-lived AWS access keys or static credentials were added.
- [ ] Trust policy examples remain scoped to the expected owner, repository, branch, tag, or environment.
- [ ] IAM permissions remain least-privilege and avoid broad administrator access.
- [ ] Production examples keep environment protection or reviewer guidance where relevant.
- [ ] Placeholder account IDs, role names, ARNs, and repository names are clearly marked.

## Documentation Checklist

- [ ] README links or repository tree were updated if files were added or moved.
- [ ] Security notes or troubleshooting guidance were updated if behaviour changed.
- [ ] The change is safe for a public reference repository and does not include private account data.

## Testing / Validation

- [ ] Markdown was reviewed for clarity.
- [ ] Workflow or IAM snippets were checked for obvious syntax issues where applicable.
