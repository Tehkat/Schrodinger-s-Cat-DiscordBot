# Privacy Policy

**Schrodinger's Cat** (the "Bot") **Effective date:** 16 November 2026

This Privacy Policy explains what information the Bot handles, why, and how you can control it. The Bot is operated by **TehKat** ("the operator", "I", "me") as a personal, non-commercial hobby project. It is designed to collect as little information as possible.

By using the Bot you agree to this Policy together with the Bot's Terms of Service.

## 1. The short version

- The Bot stores **one thing about you or your server**: the ID of each channel that has been subscribed to digests.
- It does **not** store messages, usernames, emails or any other personal details.
- It reads message content only to spot messages that start with "meow", and doesn't keep them.
- I don't sell, share, or use data for advertising or tracking.

## 2. Information the Bot handles

**a) Subscribed channel IDs (stored).** When someone runs `/subscribe`, the Bot saves that channel's numeric Discord ID in a file so it knows where to post the daily and weekly digests. Discord IDs are identifiers, not names, but I treat them with care.

**b) Article cache (stored, no user data).** The Bot keeps a cache of recent article titles, links, journal names and publication dates, retrieved from the public Crossref API, for about 30 days. This contains nothing about users.

**c) Message content (read, not stored).** The Bot has Discord's Message Content intent only so it can detect messages that begin with "meow" and reply. Messages are checked in memory as they arrive and are then discarded. They are not saved, logged, analysed or shared.

**d) Command interactions (used, not stored).** When you use a slash command, Discord sends the Bot details such as your user ID, the server ID and the channel ID so it can respond. The Bot uses these only to answer the command. Apart from the channel ID saved by `/subscribe` (see a), they are not stored.

**e) Technical logs (temporary).** The Bot's console output may briefly include operational messages such as errors and a channel ID if a digest failed to post. Logs never include message content and are not kept long-term.

## 3. How information is used

Information is used only to:

- post digests to subscribed channels,
- respond to commands, and
- keep the Bot running and fix problems.

It is not used for profiling, advertising, marketing or sale.

## 4. Third parties

- **Discord** processes data when you use the Bot on its platform, under [Discord's Privacy Policy](https://discord.com/privacy).
- **Crossref** supplies article information. The Bot sends Crossref requests for journal articles (journal ISSN numbers and date filters). **No user, server or channel information is sent.** A request may include a contact email belonging to the operator, as Crossref recommends for programmatic access.
- Article links in digests lead to publisher websites (such as nature.com) that have their own privacy practices.

I don't use analytics, trackers, advertising networks or any other third-party data processors.

## 5. Where data is kept and how it's protected

The Bot runs on a personal device in South Africa, and its data files are stored on that device. Access is limited to me, and I use reasonable measures to protect it (such as password and key-based login). The files are not encrypted at rest, and no online system is perfectly secure, so I can't guarantee absolute security.

## 6. Retention and deletion

- **Channel IDs** are kept until you run `/unsubscribe` in that channel. If the Bot is removed from a server without unsubscribing, the channel ID may remain stored (the Bot can no longer post there), and I periodically clear out stale entries.
- **Article cache** entries are deleted automatically after about 30 days.
- **Logs** are temporary and not retained long-term.

To stop the Bot storing data about your channel, run `/unsubscribe` in it and remove the Bot from your server.

## 7. Your rights

Depending on where you live, laws such as South Africa's Protection of Personal Information Act (POPIA) or the EU/UK GDPR may give you rights over your personal information, including access, correction and deletion. Because the Bot stores so little, the main control is simple: unsubscribe the channel and the stored ID is removed. If you believe the Bot holds other information about you, please tell me and I'll look into it and delete it where appropriate.

## 8. Children

The Bot is meant for people who are old enough to use Discord in their country (at least 13, or higher where local law requires). It doesn't knowingly collect information from anyone younger. If you think a child's data is stored, let me know and I'll remove it.

## 9. Changes to this Policy

I may update this Policy as the Bot changes. The effective date above will be updated when I do. Continuing to use the Bot after a change means you accept the updated Policy.

## 10. Operator

The Bot is operated by **TehKat**.