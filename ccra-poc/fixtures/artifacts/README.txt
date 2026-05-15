Artifact preview files for the CCRA POC.

In a real implementation, these would be the actual PDF / image files
of forwarded remittance emails and uploaded check scans. For the POC,
the drill-down side panel renders a text-based "preview" using the
extraction metadata so the demo flow does not require real PDF rendering
or image loading.

If you want to add real PDF/image assets, drop them in this directory
with filenames matching the artifact_ref values in the inbox/upload
manifest files. The app will display them when present and fall back to
the text preview when not.
