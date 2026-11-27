import { useLayoutEffect, useState } from 'react';

/** Live width in pixels of an element, so the map can be redrawn for the space it really has. */
export default function useBoxWidth(ref) {
  const [width, setWidth] = useState(0);
  useLayoutEffect(() => {
    const box = ref.current;
    if (!box) return undefined;
    const read = () => setWidth(box.clientWidth);
    read();
    const watcher = new ResizeObserver(read);
    watcher.observe(box);
    return () => watcher.disconnect();
  }, [ref]);
  return width;
}
