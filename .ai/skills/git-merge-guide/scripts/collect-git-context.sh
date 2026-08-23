#!/bin/sh
set -eu

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "error: current directory is not inside a Git work tree" >&2
  exit 2
fi

root=$(git rev-parse --show-toplevel)
git_dir=$(git rev-parse --git-dir)

case "$git_dir" in
  /*) ;;
  *) git_dir="$root/$git_dir" ;;
esac

exists_file() {
  [ -f "$1" ]
}

exists_dir() {
  [ -d "$1" ]
}

print_ref_if_present() {
  label=$1
  ref=$2
  if git rev-parse -q --verify "$ref" >/dev/null 2>&1; then
    printf '%s: %s\n' "$label" "$(git rev-parse "$ref")"
  fi
}

printf '%s\n' '== repository =='
printf 'root: %s\n' "$root"
printf 'head: %s\n' "$(git rev-parse HEAD)"
printf 'branch: %s\n' "$(git symbolic-ref --quiet --short HEAD 2>/dev/null || printf '%s' '(detached)')"
print_ref_if_present 'orig-head' ORIG_HEAD

printf '\n%s\n' '== operation =='
operation=none
if exists_file "$git_dir/MERGE_HEAD"; then
  operation=merge
elif exists_dir "$git_dir/rebase-merge" || exists_dir "$git_dir/rebase-apply"; then
  operation=rebase
elif exists_file "$git_dir/CHERRY_PICK_HEAD"; then
  operation=cherry-pick
elif exists_file "$git_dir/REVERT_HEAD"; then
  operation=revert
fi
printf 'active: %s\n' "$operation"

if exists_file "$git_dir/MERGE_HEAD"; then
  printf '%s\n' 'merge-heads:'
  sed 's/^/  /' "$git_dir/MERGE_HEAD"
fi

if exists_file "$git_dir/REBASE_HEAD"; then
  printf 'rebase-head: %s\n' "$(cat "$git_dir/REBASE_HEAD")"
fi

if exists_dir "$git_dir/rebase-merge"; then
  for item in head-name onto orig-head msgnum end; do
    if exists_file "$git_dir/rebase-merge/$item"; then
      printf 'rebase-%s: %s\n' "$item" "$(cat "$git_dir/rebase-merge/$item")"
    fi
  done
elif exists_dir "$git_dir/rebase-apply"; then
  for item in head-name onto orig-head next last; do
    if exists_file "$git_dir/rebase-apply/$item"; then
      printf 'rebase-%s: %s\n' "$item" "$(cat "$git_dir/rebase-apply/$item")"
    fi
  done
fi

if exists_file "$git_dir/CHERRY_PICK_HEAD"; then
  printf 'cherry-pick-head: %s\n' "$(cat "$git_dir/CHERRY_PICK_HEAD")"
fi

if exists_file "$git_dir/REVERT_HEAD"; then
  printf 'revert-head: %s\n' "$(cat "$git_dir/REVERT_HEAD")"
fi

printf '\n%s\n' '== status porcelain v2 =='
git status --porcelain=v2 --branch

printf '\n%s\n' '== unmerged paths =='
unmerged=$(git diff --name-only --diff-filter=U)
if [ -n "$unmerged" ]; then
  printf '%s\n' "$unmerged"
else
  printf '%s\n' '(none)'
fi

printf '\n%s\n' '== unmerged index stages =='
stages=$(git ls-files -u)
if [ -n "$stages" ]; then
  printf '%s\n' "$stages"
else
  printf '%s\n' '(none)'
fi

printf '\n%s\n' '== recent history =='
git log -n 12 --date=short --pretty=format:'%h %ad %d %s'
printf '\n'
