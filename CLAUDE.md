# Project instructions

## Video delivery standard (mandatory for every video editing project)

A video project is **not delivered** until the user can download and play the finished MP4 on their own computer.

1. Finish all editing, grading, transitions, motion graphics, captions, music and sound design per the approved plan.
2. Export: **1080×1920 · MP4 · H.264 · AAC · frame rate matching the source** (unless told otherwise), high quality for Instagram Reels.
3. Use a clear filename, e.g. `CLIENT_NAME_FINAL_REEL_V2.mp4`.
4. Upload the MP4 to a downloadable location (Higgsfield media upload → CloudFront URL).
5. **Attach the actual MP4** to the final response with SendUserFile (`d2ol7oe51mr4n9.cloudfront.net` is allowed in the Default environment for this).
6. Also give the verified direct download link. It must work outside the sandbox with no technical steps.
7. Before reporting delivery, verify the file exists, downloads completely (checksum matches the render) and decodes end to end.
8. Never give only a sandbox path, project ID or editing report as the deliverable.
9. Keep the original footage and the final export separate. Never overwrite source media.

**Final response format:** MP4 attachment and download link · duration · resolution and frame rate · file size · short summary of the edit · anything that could not be implemented.

## Footage project
- Upload manifest: `footage/upload-manifest.json` (media IDs, checksums, Higgsfield project).
- Draft edit lists: `footage/draft-*-edit.md`.
