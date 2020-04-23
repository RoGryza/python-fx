FROM node:12

WORKDIR /usr/src/app

COPY yarn.lock package.json ./
RUN yarn install

COPY rollup.config.js ./
RUN mkdir public
COPY ./public/index.html ./public/global.css public/
COPY src ./src

ENTRYPOINT ["yarn", "run", "dev"]
