# Unity Universal Render Pipeline (URP)

The Universal Render Pipeline (URP) is a prebuilt Scriptable Render
Pipeline made by Unity. It is designed to provide optimized graphics
performance across a wide range of platforms, from mobile devices to
high-end PCs. Unlike the Built-in Render Pipeline, URP is highly
customizable and relies on a modern, single-pass forward rendering loop.

A key feature of URP is the ability to extend its functionality using
ScriptableRenderPass components. Developers can inject custom rendering
commands -- such as screen-space outlines, custom post-processing
effects, or specialized lighting calculations -- at specific points in
the render loop. Adjusting the RenderGraph in URP gives technical artists
deep control over how a frame is constructed before it reaches the
screen.
