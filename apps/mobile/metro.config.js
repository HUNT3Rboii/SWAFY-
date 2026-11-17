// Metro (the bundler) settings for the SWAFY monorepo.
// The app imports @swafy/api-client from packages/api-client, which is outside
// apps/mobile, so Metro must watch that folder and find its dependencies
// (openapi-fetch) in apps/mobile/node_modules.
const path = require('path');
const { getDefaultConfig } = require('expo/metro-config');

const projectRoot = __dirname;
const monorepoRoot = path.resolve(projectRoot, '../..');

const config = getDefaultConfig(projectRoot);

config.watchFolders = [...(config.watchFolders ?? []), path.resolve(monorepoRoot, 'packages/api-client')];
config.resolver.nodeModulesPaths = [path.resolve(projectRoot, 'node_modules')];

module.exports = config;
