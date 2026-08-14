# Environment Discovery

## VCS Role Mapping

Treat base, branch, commit, remote, detached state, and pending changes as semantic roles rather than required native primitives. Map each role to the discovered state-management capability's native model and operations, and record unsupported roles as unavailable. A role name never implies a provider, client, command, or workspace mechanism.

## Ordered Discovery

1. Read applicable project instructions, declared documentation, and available project-native capabilities before selecting an operation. Record facts separately from inferences and each unavailable capability with its reason.
2. Discover state management, issue retrieval, remote synchronization, and review publication independently. Do not infer one capability from another or assume a provider, client, or conventional base name.
3. For ticket input, acquire its description, acceptance criteria, relevant discussion, and canonical identifier through an available issue capability. On failure, retain the literal identifier and accompanying text, record the limitation, and continue with locally available evidence.

## Base and Workspace

Determine the semantic base from authoritative project metadata first, then remote default or upstream relationship, and use conventional naming only as fallback evidence. Synchronize it when a supported remote capability exists; otherwise retain the verified local base and record the limitation.

Use the exact canonical ticket identifier as the task branch identity when accepted by the discovered state-management capability. Otherwise apply the smallest deterministic normalization and record the mapping. For raw text, derive a short factual slug without inventing scope.

Resume an existing matching local or remote task workspace only when its assignment identity and provenance agree with the manifest. For a same-name collision with unknown or conflicting provenance, choose a deterministic suffix and record the collision. Use an environment-native isolated workspace when declared; otherwise use the clean task workspace supported by the environment.

## Prior State and Gaps

Inspect pending state through the mapped capability before task provisioning. Preserve any prior state through finishing in preservation mode. If dirty state lacks reversible preservation, ignore-state inspection, or content inspection, record an unsafe blocker and do not begin task work. Stop preservation or publication on detected credentials, private keys, or tokens with path evidence.

Without usable state-management capability, a clean workspace may execute a raw-text assignment and produce local verification artifacts; record branch, commit, synchronization, and review publication as unavailable. Missing issue, remote, or review capability degrades to local completion rather than simulation.

For review publication, reuse a matching active request when supported; otherwise create a draft, unassigned request that follows discovered templates and does not notify reviewers. When draft state is unavailable, create an unassigned non-draft request only when authoritative platform semantics prove it is non-notifying. Otherwise record review publication as unavailable.
