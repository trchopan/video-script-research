# video-script-research

A simple helper tool for me to research about a particular project. Use Youtube as a content resource for the research.

Features:

- Use Vector database to find similarity meaning in the transcript from Youtube.
- General knowledge from Wikipedia
- Extends scripts by context in Scratch Pad

# Build note

If building in a pyenv need to activate some environment variables:

```bash
GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=true GRPC_PYTHON_BUILD_SYSTEM_ZLIB=true pip install google-cloud-speech
```
