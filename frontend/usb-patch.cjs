const fs = require('fs');
const path = require('path');

// Ensure all child processes & worker threads inherit this patch
const patchPath = path.resolve(__dirname, 'usb-patch.cjs').replace(/\\/g, '/');
if (!process.env.NODE_OPTIONS || !process.env.NODE_OPTIONS.includes('usb-patch.cjs')) {
  process.env.NODE_OPTIONS = `${process.env.NODE_OPTIONS ? process.env.NODE_OPTIONS + ' ' : ''}-r ${patchPath}`;
}

// Patch for Windows FAT32/exFAT USB drives:
// On non-NTFS volumes, readlink on regular files produces EISDIR instead of EINVAL.
const patchErr = (err) => {
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
      return cb(patchErr(err), linkString);
    };
  }
  return origReadlink.call(fs, path, ...args);
};

const origReadlinkSync = fs.readlinkSync;
fs.readlinkSync = function (path, options) {
  try {
    return origReadlinkSync.call(fs, path, options);
  } catch (err) {
    throw patchErr(err);
  }
};

if (fs.promises && fs.promises.readlink) {
  const origPromisesReadlink = fs.promises.readlink;
  fs.promises.readlink = async function (path, options) {
    try {
      return await origPromisesReadlink.call(fs.promises, path, options);
    } catch (err) {
      throw patchErr(err);
    }
  };
}
