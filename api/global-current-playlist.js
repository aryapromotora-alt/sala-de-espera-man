import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

const GLOBAL_SESSION_ID = 'global_default';

export default async function handler(req, res) {
  const path = req.url.split('/').pop();

  if (req.method === 'GET') {
    let { data: sessionData } = await supabase
      .from('user_sessions')
      .select('*')
      .eq('session_id', GLOBAL_SESSION_ID);

    if (!sessionData || sessionData.length === 0) {
      await supabase.from('user_sessions').insert({ session_id: GLOBAL_SESSION_ID });
      await supabase.from('playlists').insert({
        name: 'default',
        user_id: GLOBAL_SESSION_ID,
        items: [],
      });

      ({ data: sessionData } = await supabase
        .from('user_sessions')
        .select('*')
        .eq('session_id', GLOBAL_SESSION_ID));
    }

    const { data: playlistsData } = await supabase
      .from('playlists')
      .select('*')
      .eq('user_id', GLOBAL_SESSION_ID);

    const playlistsDict = {};
    for (const p of playlistsData || []) {
      let items = [];
      try {
        items = Array.isArray(p.items) ? p.items : JSON.parse(p.items);
      } catch {
        items = [];
      }
      playlistsDict[p.name] = items;
    }

    return res.status(200).json({
      success: true,
      playlists: playlistsDict,
      current_playlist: sessionData[0]?.current_playlist || 'default',
    });
  }

  if (req.method === 'PUT') {
    let data;
    try {
      data = req.body;
    } catch {
      return res.status(400).json({ error: 'Invalid JSON' });
    }

    if (!path || path === 'global-playlists') {
      return res.status(400).json({ error: 'Playlist name is required' });
    }

    const playlistName = path;
    const items = data.items || [];

    const { data: playlistData } = await supabase
      .from('playlists')
      .select('*')
      .eq('user_id', GLOBAL_SESSION_ID)
      .eq('name', playlistName);

    let playlist;
    if (!playlistData || playlistData.length === 0) {
      const { data: newPlaylist } = await supabase
        .from('playlists')
        .insert({ name: playlistName, user_id: GLOBAL_SESSION_ID, items })
        .select();
      playlist = newPlaylist[0];
    } else {
      const { data: updated } = await supabase
        .from('playlists')
        .update({ items })
        .eq('user_id', GLOBAL_SESSION_ID)
        .eq('name', playlistName)
        .select();
      playlist = updated[0];
    }

    return res.status(200).json({
      success: true,
      playlist,
    });
  }

  if (req.method === 'DELETE') {
    if (!path || path === 'global-playlists') {
      return res.status(400).json({ error: 'Playlist name is required' });
    }

    const playlistName = path;

    if (playlistName === 'default') {
      return res.status(400).json({ error: 'Cannot delete default playlist' });
    }

    const { data: playlistData } = await supabase
      .from('playlists')
      .select('*')
      .eq('user_id', GLOBAL_SESSION_ID)
      .eq('name', playlistName);

    if (!playlistData || playlistData.length === 0) {
      return res.status(400).json({ error: 'Playlist not found' });
    }

    await supabase
      .from('playlists')
      .delete()
      .eq('user_id', GLOBAL_SESSION_ID)
      .eq('name', playlistName);

    const { data: sessionData } = await supabase
      .from('user_sessions')
      .select('*')
      .eq('session_id', GLOBAL_SESSION_ID);

    if (sessionData?.[0]?.current_playlist === playlistName) {
      await supabase
        .from('user_sessions')
        .update({ current_playlist: 'default' })
        .eq('session_id', GLOBAL_SESSION_ID);
    }

    return res.status(200).json({
      success: true,
      message: 'Playlist deleted successfully',
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