import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

async function seedBriefs() {
  const supabase = createClient(supabaseUrl, supabaseKey)

  // First, get or create a test user
  const { data: users } = await supabase.from('users').select('id').limit(1)

  if (!users || users.length === 0) {
    console.error('No users found. Please onboard a user first.')
    return
  }

  const userId = users[0].id
  console.log('Seeding briefs for user:', userId)

  const today = new Date().toISOString().split('T')[0]
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0]

  // Today's morning brief
  const morningBrief = {
    user_id: userId,
    type: 'morning',
    date: today,
    content: {
      summary:
        "Howdy partner! Markets are looking mighty fine today with SGX showing strong momentum. The STI is positioned near key support levels, and we've got some exciting opportunities brewing in the banking sector.",
      market_overview:
        "STI opened 0.3% higher at 3,245 points, following positive cues from Wall Street's overnight rally. Banking stocks are leading the charge with DBS up 1.2% in pre-market trading. Regional markets showing mixed signals with Hong Kong flat and Japan up 0.5%.",
      key_points: [
        'DBS announces strong Q4 earnings, beating analyst expectations by 8%',
        "Singapore's GDP growth revised upward to 3.2%, supporting local equities",
        'Tech sector under pressure as US chip restrictions impact regional suppliers',
        'Real Estate Investment Trusts (REITs) gaining traction amid stable interest rates',
        'Watch out for Fed Chair speech at 10PM SGT - could impact Asian markets tomorrow',
      ],
      recommendations: [
        'DBS Group Holdings (D05) - Strong buy on earnings beat. Entry: $35.20, Target: $37.50',
        'CapitaLand Investment (9CI) - Accumulate on REIT strength. Entry: $3.15, Target: $3.45',
        'Venture Corp (V03) - Monitor for oversold bounce. Entry: $15.80, Stop: $15.20',
      ],
    },
  }

  // Today's EOD brief
  const eodBrief = {
    user_id: userId,
    type: 'eod',
    date: today,
    content: {
      summary:
        "Another day in the saddle, partner! Your portfolio rode well today with solid gains across most positions. The market gave us exactly what we expected - steady gains in banks and some volatility in tech.",
      market_overview:
        'STI closed up 0.45% at 3,259 points, with banking stocks leading the charge. Volume was above average at 1.2B shares traded. Regional markets ended mixed with Hong Kong down 0.3% and Japan up 0.8%.',
      key_points: [
        "Your DBS position up 1.5% today, contributing $450 to daily P&L",
        'Tech stocks pulled back as expected, but positions held support levels',
        "Banking sector momentum likely to continue into tomorrow's session",
        'Watch for potential profit-taking in early trading tomorrow',
        'Overall risk exposure remains within your conservative profile limits',
      ],
      portfolio_summary: {
        total_value: '$52,450',
        daily_pnl: '+$685 (+1.3%)',
        positions: 5,
      },
    },
  }

  // Yesterday's briefs
  const yesterdayMorning = {
    user_id: userId,
    type: 'morning',
    date: yesterday,
    content: {
      summary:
        'Good morning, partner! Markets opened cautiously yesterday as investors digested mixed economic data. The STI showed resilience despite regional headwinds.',
      market_overview:
        'STI started flat at 3,235 points. Banking sector showed strength while tech lagged. Regional markets were mixed with profit-taking in Hong Kong.',
      key_points: [
        'Banking sector maintained stability despite rate concerns',
        'Tech stocks faced selling pressure on valuation concerns',
        'Real estate sector showed mixed signals',
        'Foreign institutional flows remained positive',
        'Oil prices stabilized, supporting energy stocks',
      ],
      recommendations: [
        'OCBC Bank (O39) - Accumulate on dips. Entry: $13.50, Target: $14.00',
        'Keppel Corp (BN4) - Watch for energy sector strength. Entry: $6.80',
      ],
    },
  }

  const yesterdayEOD = {
    user_id: userId,
    type: 'eod',
    date: yesterday,
    content: {
      summary:
        'Markets closed slightly down yesterday, partner. Nothing to worry about - just healthy consolidation after recent gains. Your portfolio held up well.',
      market_overview:
        'STI closed down 0.25% at 3,227 points. Volume was below average at 950M shares. Tech weakness offset banking strength.',
      key_points: [
        'Portfolio down slightly but outperformed the index',
        'Banking positions provided good defense',
        'Tech positions near key support levels',
        'No major risk events triggered',
        'Overall positioning remains healthy',
      ],
      portfolio_summary: {
        total_value: '$51,765',
        daily_pnl: '-$235 (-0.45%)',
        positions: 5,
      },
    },
  }

  // Insert all briefs
  const briefs = [morningBrief, eodBrief, yesterdayMorning, yesterdayEOD]

  for (const brief of briefs) {
    const { data, error } = await supabase.from('briefs').upsert(brief, {
      onConflict: 'user_id,type,date',
    })

    if (error) {
      console.error(`Error seeding ${brief.type} brief for ${brief.date}:`, error)
    } else {
      console.log(`✅ Seeded ${brief.type} brief for ${brief.date}`)
    }
  }

  console.log('✅ Done seeding briefs!')
}

seedBriefs().catch(console.error)

