import fs from 'fs';

// ==============================================================================
// USB Drive Filesystem Compatibility Patch (Windows exFAT / FAT32)
// On Windows non-NTFS volumes, Node.js readlink returns EISDIR instead of EINVAL
// on regular files. Webpack expects EINVAL or UNKNOWN to treat files as non-symlinks.
// ==============================================================================
const patchReadlinkError = (err) => {
  if (err && (err.code === 'EISDIR' || err.code === 'UNKNOWN')) {
    err.code = 'EINVAL';
  }
  return err;
};

const origReadlink = fs.readlink;
fs.readlink = function (path, ...args) {
  const cb = args[args.length - 1];
  if (typeof cb === 'function') {
    args[args.length - 1] = function (err, linkString) {
      return cb(patchReadlinkError(err), linkString);
    };
  }
  return origReadlink.call(fs, path, ...args);
};

const origReadlinkSync = fs.readlinkSync;
fs.readlinkSync = function (path, options) {
  try {
    return origReadlinkSync.call(fs, path, options);
  } catch (err) {
    throw patchReadlinkError(err);
  }
};

if (fs.promises && fs.promises.readlink) {
  const origPromisesReadlink = fs.promises.readlink;
  fs.promises.readlink = async function (path, options) {
    try {
      return await origPromisesReadlink.call(fs.promises, path, options);
    } catch (err) {
      throw patchReadlinkError(err);
    }
  };
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: process.env.BUILD_STANDALONE === 'true' || process.env.DOCKER_BUILD === 'true' ? 'standalone' : undefined,
  webpack: (config) => {
    config.resolve.symlinks = false;
    return config;
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://127.0.0.1:8000/api/v1/:path*',
      },
    ];
  },
};

export default nextConfig;
