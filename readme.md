## Sportnumerics Rankings

This will be an attempt to unify and re-write some of the sportnumerics codebase.

The major components will still be:
1. Fetching Stats from NCAA / MCLA
2. Pre-process
3. Calculate ratings
4. Post-process
5. Create static assets

However, this time I'd like to be able to move things around between the steps a bit easier, which will make it more flexible, and empower experimentation. I'd like to make it really easy to run parts of the pipeline locally. In addition, I'd like to make it easy to see what changed through the course of the season, so capturing changes over time - i.e. build the ratings based on a specific set of inputs.

I'd like to organise the project around a python executable with modules. Then I can run that exec anywhere, in docker, or locally.

~I'd also like to move away from react, and ideally just create static html from the pipeline itself and serve that from S3 with a CDN to make it super fast.~

Ok had to scratch that because React is just so much easier.

### Structure

    /infrastructure

Shared resources like the target S3 bucket.

    /backend

Backend for scraping and predicting rankings

    /frontend

Next.js UI for rendering the output in the browser.
