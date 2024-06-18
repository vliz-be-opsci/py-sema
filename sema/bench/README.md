(current sembench) – focus on the task-orchestration and scheduling
should have a main too, and be a callable (nested? → 0.0.5) service thing itself
to expose that __main__ as script wrapper "sema-bench" (poetry run python -m sema.bench {args} → poetry run sema-bench {args} )
to solve relative path resolution in the config to various services→ keep current rel path solution
to foresee some mechanism to have external 'service-tasks' be included and executable as part of the sema-bench chain  (e.g provided through custom code in a k-gap project – like the odsg tool) → make issue post 0.0.4 ( for 0.0.5 implementation)
