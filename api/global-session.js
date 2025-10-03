import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

export default async function handler(req, res) {
  if (req.method === 'POST') {
    let data = {};
    try {
      data = req.body;
    } catch {
      data = {};
    }

    const globalSessionId = data.global_session_id || 'global_default';

    let { data: sessionData } = await supabase
      .from('user_sessions')
      .select('*')
      .eq('session_id', globalSessionId);

    if (!sessionData || sessionData.length === 0) {
      await supabase.from('user_sessions').insert({ session_id: globalSessionId });
      await supabase.from('playlists').insert({
        name: 'default',
        user_id: globalSessionId,
        items: [],
      });

      ({ data: sessionData } = await supabase
        .from('user_sessions')
        .select('*')
        .eq('session_id', globalSessionId));
    }

    return res.status(200).json({
      success: true,
      session: sessionData[0],
    });
  }

  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }

  return res.status(405).json({ error: 'Method not allowed' });
}