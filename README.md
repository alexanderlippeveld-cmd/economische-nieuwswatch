# Economische nieuwswatch

Een gratis, statische economische nieuwswatch die draait op GitHub Pages en dagelijks wordt bijgewerkt met GitHub Actions.

## Wat deze MVP doet

- haalt openbare RSS/Atom-feeds op;
- bewaart alleen titel, link, bron, datum en publiek beschikbare samenvatting;
- dedupliceert artikels;
- deelt artikels thematisch in;
- maakt een korte Nederlandstalige briefing met een lokale, extractieve samenvatter;
- markeert trefwoorden;
- biedt zoeken, themafilters, leesstatus, leeslijst en notities;
- bewaart persoonlijke acties lokaal in de browser via `localStorage`;
- publiceert automatisch naar GitHub Pages.

## Gratis architectuur

- **Hosting:** GitHub Pages
- **Automatisering:** GitHub Actions
- **Datastore:** JSON-bestanden in `docs/data/`
- **Frontend:** statische HTML, CSS en JavaScript
- **Samenvatting:** lokale heuristiek, dus geen betaalde AI-API nodig

GitHub Copilot kan je gebruiken om de code verder te ontwikkelen. Copilot is hier geen runtime-API. Wil je later betere AI-samenvattingen, voeg dan in `scripts/build_briefing.py` een provider toe en bewaar de sleutel als GitHub Actions secret.

## Installatie

1. Maak een nieuwe **publieke** GitHub-repository.
2. Upload de inhoud van deze map naar de hoofdmap van de repository.
3. Ga naar **Settings > Pages**.
4. Kies bij **Build and deployment**: **Deploy from a branch**.
5. Kies branch `main` en map `/docs`.
6. Open **Actions**, kies `Dagelijkse nieuwswatch` en klik op **Run workflow**.
7. De site staat daarna op `https://<gebruikersnaam>.github.io/<repository>/`.

De workflow draait ook elke ochtend om 06:15 UTC. In België is dat 08:15 tijdens de zomertijd en 07:15 tijdens de wintertijd.

## Lokaal testen

```bash
python scripts/build_briefing.py
python -m http.server 8000 --directory docs
```

Open daarna `http://localhost:8000`.

## Bronnen aanpassen

Pas `sources.json` aan. Elke bron heeft:

```json
{
  "name": "Voorbeeld",
  "url": "https://example.com/feed.xml",
  "region": "BE",
  "paywall": false
}
```

Een mislukte feed breekt de run niet. De fout verschijnt in het Actions-log.

## Trefwoorden aanpassen

Pas `keywords.json` aan. Gebruikers kunnen daarnaast browser-lokale trefwoorden toevoegen in de interface.

## Belangrijke beperkingen

- Dit is een persoonlijke MVP, geen multi-user SaaS.
- Leeslijst, notities en gelezen-status blijven in één browserprofiel.
- GitHub Pages heeft geen database of login.
- RSS-feeds en hun voorwaarden kunnen wijzigen.
- Publiceer geen volledige betaalde artikels. Deze code bewaart alleen feedmetadata en publiek beschikbare snippets.
- Controleer voor professioneel gebruik de gebruiksvoorwaarden en robotsregels van elke bron.

## Naar versie 2

Voor accounts en synchronisatie kun je later Supabase Free toevoegen. Voor betere clustering kun je embeddings of een LLM-provider gebruiken. Houd API-sleutels altijd in GitHub Secrets en nooit in frontendcode.
