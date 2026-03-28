export default async function handler(req) {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  try {
    const { email } = await req.json();

    if (!email || !email.includes("@")) {
      return new Response(JSON.stringify({ error: "invalid email" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Visible in `vercel logs`. Wire up a real store when needed.
    console.log(`[notify] ${email} ${new Date().toISOString()}`);

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return new Response(JSON.stringify({ error: "bad request" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }
}

export const config = { runtime: "edge" };
