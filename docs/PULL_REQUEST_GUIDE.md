# Your first pull request for this clock

A pull request (PR) asks the original project's maintainer to review and merge changes from your fork. Your changes are first saved as commits on a branch, then pushed to your GitHub fork. The maintainer decides whether to merge the PR. Opening one does not itself change the original project.

This guide prepares a **draft PR** so you can review the comparison and add hardware results before requesting a merge. This guide uses `dev` as the contribution branch. Use `git status` and `git branch -vv` to check which preparation steps have already been completed in your checkout. Creating the PR on GitHub is a separate step.

## 1. Understand the two repositories

The remotes already configured in this checkout are:

| Name | Repository | Role |
| ---- | ---------- | ---- |
| `origin` | [anthonyjclarke/ESP32-max7219-Matrix-Clock](https://github.com/anthonyjclarke/ESP32-max7219-Matrix-Clock) | Your fork; push your branch here. |
| `upstream` | [OlLiLe18/ESP32-max7219-Matrix-Clock](https://github.com/OlLiLe18/ESP32-max7219-Matrix-Clock) | Original project; target its `main` branch in the PR. |

At preparation time on 23 October 2026, local `main` was at `5a35904`, one commit ahead of the locally recorded `origin/main`. Three fork commits were ahead of the shared ancestor; upstream had ten separate commits after that ancestor. Runtime settings, date/year, language, helper, and test changes were still uncommitted. That was the initial preparation snapshot; `dev` is the branch used to publish the completed code and documentation. Check `git status` for any remaining edits. GitHub may have changed since the snapshot; the fetch step below refreshes the comparison.

Upstream has already added English documentation and moved the clock image into `images/`. A read-only merge preview of the committed branches found a README conflict. The steps below explain how to handle that without discarding your saved work.

## 2. Create a branch for the contribution

Open a terminal in this project directory. In VS Code, **Terminal → New Terminal** normally opens there. Check:

```sh
git status
git remote -v
```

Create a new branch from the current checkout:

```sh
git switch -c dev
```

The branch starts with your existing commits, and the pending file changes stay with you. You do not need another fork or a new repository. If this branch already exists, use `git switch dev` and check its status before continuing.

## 3. Save the pending work in a commit

Stage the project and documentation files explicitly:

```sh
git add README.md ESPHOME_VALIDATION.md secrets.example.yaml \
  max7219-esp32-reg.yaml max7219-esp32c3-supermini.yaml clock_settings.h \
  scripts/check_display_logic.py scripts/check_runtime_settings.py \
  docs/FORK_CHANGES.md docs/PULL_REQUEST_GUIDE.md docs/PULL_REQUEST_DESCRIPTION.md \
  docs/images/esphome-web-ui.png
git diff --cached --stat
git diff --cached
```

The first review shows which files will be committed; the second shows their actual changes. Include the new header and runtime test script, since untracked files do not get published automatically. Your private `secrets.yaml` is ignored by Git; it and `.DS_Store` should not appear in this staged file list. The sample secrets file should contain placeholders.

Save the staged work:

```sh
git commit -m "Add configurable clock settings, date year, and weekday language"
```

This creates a local checkpoint. It has not uploaded anything to GitHub. The previous C3 and compatibility commits are already part of this branch's history and will also be included in the PR comparison.

## 4. Bring in the original project's latest changes

After committing your work, run:

```sh
git fetch origin
git fetch upstream
git merge upstream/main
```

Use an ordinary merge for this first contribution. It preserves the existing commits and avoids rewriting branch history. Fetching downloads remote history; merging incorporates the original project's changes into your contribution branch.

### If Git reports a README conflict

Run `git status` to see the unresolved files. In VS Code, open `README.md` from Source Control's **Merge Changes** list. The editor may show a merge editor or conflict markers. A line starting with `<<<<<<< HEAD` introduces your branch's text, `=======` separates the versions, and `>>>>>>> upstream/main` ends upstream's text.

Edit the resulting README so it contains the intended final text, then remove all conflict markers. For this upstream contribution:

- Preserve the original author's attribution, German/English documentation, and newer upstream material.
- Add the new C3, runtime settings, year, and weekday-language instructions where appropriate; this fork's full README version remains available in the commit you just made.
- Use the resulting image location, normally `images/Clock max7219 (2).png`, and check that its README link works.
- Rewrite fork-specific introductory wording so the README makes sense in the original repository. Link to `docs/FORK_CHANGES.md` and `ESPHOME_VALIDATION.md` for implementation and validation details.

Do not choose **Accept All Current** or **Accept All Incoming** without reviewing what would be lost. When the README is resolved, and `git status` shows no other unresolved files:

```sh
git add README.md
git commit -m "Merge upstream documentation updates"
```

If other files conflict, resolve them before completing the merge. To cancel an unfinished merge and return to the checkpoint from step 3, use:

```sh
git merge --abort
```

An unresolved merge must be completed or aborted before continuing. Neither option requires deleting your branch or starting the project again.

## 5. Verify the resulting contribution

Review the changes against the updated upstream branch:

```sh
git log --oneline upstream/main..HEAD
git diff --stat upstream/main...HEAD
git diff upstream/main...HEAD
python3 scripts/check_display_logic.py
```

Confirm the new header and test script are included, the image move is preserved, and the code changes match the [fork summary](./FORK_CHANGES.md). This comparison should describe your contribution rather than undo unrelated upstream edits.

In a Python environment with ESPHome installed, run:

```sh
esphome config max7219-esp32-reg.yaml
esphome config max7219-esp32c3-supermini.yaml
esphome compile max7219-esp32c3-supermini.yaml
python3 scripts/check_runtime_settings.py
```

These commands require the fonts, header, and appropriate local secrets. ESPHome Device Builder can also perform configuration validation and compilation using your Home Assistant files. If you edit firmware while resolving conflicts, repeat the checks that cover those edits. Record new results in `ESPHOME_VALIDATION.md` and update the PR description if the scope or results change.

The current documented results include a successful C3 build and software simulations; physical hardware checks remain pending. A draft PR can state that plainly. Add your board, ESPHome version, and observed results when you have tested it. A successful build alone does not establish that the physical clock works.

If you make further edits during verification, stage the named files and create another commit before pushing.

## 6. Push the branch to your fork

```sh
git push -u origin dev
```

This uploads the branch to **your fork**, not to the original repository. If GitHub asks you to sign in, use the authentication method configured for Git on your computer. You can confirm the branch on your fork's GitHub page using its branch dropdown.

## 7. Open the draft PR in your browser

After the push, open this [prepared comparison](https://github.com/OlLiLe18/ESP32-max7219-Matrix-Clock/compare/main...anthonyjclarke:dev?expand=1). It will become useful once the branch has been pushed.

Alternatively, open the original repository's **Pull requests → New pull request**, then select **compare across forks**. Check these four fields:

| Field | Value |
| ----- | ----- |
| Base repository | `OlLiLe18/ESP32-max7219-Matrix-Clock` |
| Base branch | `main` |
| Head repository | `anthonyjclarke/ESP32-max7219-Matrix-Clock` |
| Compare branch | `dev` |

The base receives the proposed changes; the head contains them. If both repositories are your fork, you are proposing a change within your own fork instead of contributing to the original project.

Review **Files changed**. Paste the title and description from [`PULL_REQUEST_DESCRIPTION.md`](./PULL_REQUEST_DESCRIPTION.md), omitting its “Suggested title” and “Suggested description” labels. Adjust any statements affected by your merge resolution or hardware testing. Use the dropdown beside the create button to choose **Create draft pull request**, then submit it.

GitHub's official [fork PR instructions](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request-from-a-fork) explain the base/head selection and draft option. A [draft PR](https://docs.github.com/en/pull-requests/reference/pull-requests#draft-pull-requests) shares work for discussion while keeping it from being merged until it is marked ready.

## 8. Respond to review

If the maintainer requests changes, edit the same local branch, commit the affected files, and run:

```sh
git push
```

The existing PR updates automatically. Use its **Conversation** tab to explain the adjustment and test result. You do not need to create another PR for each revision. The maintainer may prefer the compatibility fixes and new features in separate PRs; the [change summary](./FORK_CHANGES.md) separates them so that discussion is easier.

When your intended checks are complete and the description reflects the final changes, use **Ready for review**. The original maintainer controls acceptance and merging. You can track discussion, commits, automated checks if any, and the final diff on the PR page.
