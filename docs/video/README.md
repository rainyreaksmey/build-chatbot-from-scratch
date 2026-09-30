# Render the tutorial video

The rendered 30-second video is included as `chatbot-intro.mp4`. The existing
repository also contains its Remotion source and dependencies. The
`ChatbotIntro` composition is registered there so no second JavaScript project
or duplicate dependency installation is needed when you want to modify it.

From the repository root:

```bash
cd video
npx remotion render src/index.ts ChatbotIntro ../chatbot/docs/video/chatbot-intro.mp4 \
  --codec=h264 --crf=22 --muted
```

To preview it interactively:

```bash
cd video
npm run dev
```

Choose **ChatbotIntro** in Remotion Studio.
