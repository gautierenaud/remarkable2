# remarkable ssh Driver

Here I come again, this time with a driver based on ssh.

It mainly comes from the fact that remarkable's cloud API keeps changing, and at this point I guess "why not ssh everything ?".

Hints:
* calibre plugin using OpenWith -> "hey, we can just use subprocesses, so why not ssh?"
* https://github.com/reHackable/scripts: "Oi, there are already scripts that push/pull books!"
    * naming changed
        * found a fork that seems to patch (at least partially) the issue
    * not working with latest naming conventions
        * before file was named after metadata
        * now it seeks the name in the file itself (at least for epub)
            * tested by generating an empty book with Calibre and fiddling with the title
        * -> Generate a placeholder ebook with the right title (maybe a unique hash? Or the metadata won't be regenerated...)
            * worst case scenario: just curl the ebook and don't use scp at all

# Pushing books

1) put a placeholder through the web interface (`/upload`)
2) once metadata files are created, scp the whole book and update metadata

## Tests

### Get list of books

Print filenames that are "DocumentType":
```bash
❯ ssh root@10.11.99.1 'find /home/root/.local/share/remarkable/xochitl/ -type f -name "*.metadata" -exec grep -qw "DocumentType" {} \; -print'
/home/root/.local/share/remarkable/xochitl/238a575f-474a-41ac-a692-a908461c8b2b.metadata
/home/root/.local/share/remarkable/xochitl/1bbfa098-6f28-4d73-85c9-84bab6823ad2.metadata
/home/root/.local/share/remarkable/xochitl/0fff5161-fb57-42f5-a116-2332c2273219.metadata
/home/root/.local/share/remarkable/xochitl/2a33df84-a266-4e45-9e77-057d4d0f0dd6.metadata
/home/root/.local/share/remarkable/xochitl/433ddb26-0927-4500-ab59-64384a8f5eac.metadata
/home/root/.local/share/remarkable/xochitl/b65b42ae-1de1-4e62-bbb2-38db822369c3.metadata
/home/root/.local/share/remarkable/xochitl/ceda710f-88fc-4480-b528-5bc631702a75.metadata
/home/root/.local/share/remarkable/xochitl/ab2cf923-d76a-410c-881b-8fe2286096cd.metadata
/home/root/.local/share/remarkable/xochitl/ebca512c-99d8-47a8-9cd5-45d9b288fcad.metadata
/home/root/.local/share/remarkable/xochitl/da7aee5d-32a7-45e5-9cd7-13fe1256a7bf.metadata
/home/root/.local/share/remarkable/xochitl/2db98d03-f8a0-4573-8c68-fe57b2f22f86.metadata
/home/root/.local/share/remarkable/xochitl/6518a8c9-5110-4e3c-9c11-72e2a9cb30b3.metadata
/home/root/.local/share/remarkable/xochitl/76209de6-d49c-4880-a6a0-45aefbec999e.metadata
/home/root/.local/share/remarkable/xochitl/545c8882-1efc-4500-b09d-cbd70e9fdb89.metadata
/home/root/.local/share/remarkable/xochitl/c5eddb4b-9f99-4d0f-bbbd-ec8752bbbc32.metadata
/home/root/.local/share/remarkable/xochitl/f464e0ba-9021-4ab6-95bd-631a015133a9.metadata
/home/root/.local/share/remarkable/xochitl/2d66256c-35df-4398-a3c3-8083d63c546a.metadata
/home/root/.local/share/remarkable/xochitl/63566dae-458e-4343-b047-3b75f81fbd7f.metadata
/home/root/.local/share/remarkable/xochitl/d7807e58-f473-4a61-a34c-39f2c63f0c15.metadata
/home/root/.local/share/remarkable/xochitl/13df9036-e63d-41fb-8861-7bb7a8383683.metadata
/home/root/.local/share/remarkable/xochitl/3ce13086-8125-4440-aea9-c4e749963e84.metadata
/home/root/.local/share/remarkable/xochitl/5490a0fe-6e95-4e44-a674-31a9de2d3d90.metadata
/home/root/.local/share/remarkable/xochitl/a7d1143a-ccc9-451d-8464-de6e468252a6.metadata
/home/root/.local/share/remarkable/xochitl/7654cd66-bd0a-4b2d-8ea5-8fd35daba9c0.metadata
/home/root/.local/share/remarkable/xochitl/06916f31-0c7b-4572-ba26-1b27e08e13fa.metadata
/home/root/.local/share/remarkable/xochitl/04c63424-ee52-4b31-8027-e21548a764e5.metadata
/home/root/.local/share/remarkable/xochitl/39bad5e3-c0be-4f35-99de-b1388408172d.metadata
```

```bash
❯ ssh root@10.11.99.1 'cat /home/root/.local/share/remarkable/xochitl/ebca512c-99d8-47a8-9cd5-45d9b288fcad.metadata'
{
    "deleted": false,
    "lastModified": "1623232982000",
    "lastOpened": "1623232982000",
    "lastOpenedPage": 5,
    "metadatamodified": false,
    "modified": false,
    "parent": "38d6ea4d-77a6-4004-82f7-423ea0196f72",
    "pinned": false,
    "synced": true,
    "type": "DocumentType",
    "version": 3,
    "visibleName": "gunnm_1"
}
```

What I want for each DocumentType file:
* own id
* visible name


```bash
❯ ssh root@10.11.99.1 'find /home/root/.local/share/remarkable/xochitl/ -type f -name "*.metadata" -exec grep -qw "DocumentType" {} \; -exec grep "visibleName" {} \; -print'
    "visibleName": "Jeu societe"
/home/root/.local/share/remarkable/xochitl/238a575f-474a-41ac-a692-a908461c8b2b.metadata
    "visibleName": "gunnm_2"
/home/root/.local/share/remarkable/xochitl/1bbfa098-6f28-4d73-85c9-84bab6823ad2.metadata
    "visibleName": "Guardening"
/home/root/.local/share/remarkable/xochitl/0fff5161-fb57-42f5-a116-2332c2273219.metadata
    "visibleName": "Tales of Known Space - Larry Niven"
/home/root/.local/share/remarkable/xochitl/2a33df84-a266-4e45-9e77-057d4d0f0dd6.metadata
    "visibleName": "A Canticle for Leibowitz"
/home/root/.local/share/remarkable/xochitl/433ddb26-0927-4500-ab59-64384a8f5eac.metadata
    "visibleName": "Drawing"
/home/root/.local/share/remarkable/xochitl/b65b42ae-1de1-4e62-bbb2-38db822369c3.metadata
    "visibleName": "Note taking"
/home/root/.local/share/remarkable/xochitl/ceda710f-88fc-4480-b528-5bc631702a75.metadata
    "visibleName": "gunnm_9"
/home/root/.local/share/remarkable/xochitl/ab2cf923-d76a-410c-881b-8fe2286096cd.metadata
    "visibleName": "gunnm_1"
/home/root/.local/share/remarkable/xochitl/ebca512c-99d8-47a8-9cd5-45d9b288fcad.metadata
    "visibleName": "Red Rising 4: Iron Gold"
/home/root/.local/share/remarkable/xochitl/da7aee5d-32a7-45e5-9cd7-13fe1256a7bf.metadata
    "visibleName": "gunnm_3"
/home/root/.local/share/remarkable/xochitl/2db98d03-f8a0-4573-8c68-fe57b2f22f86.metadata
    "visibleName": "histoire"
/home/root/.local/share/remarkable/xochitl/6518a8c9-5110-4e3c-9c11-72e2a9cb30b3.metadata
    "visibleName": "mashi mashi"
/home/root/.local/share/remarkable/xochitl/76209de6-d49c-4880-a6a0-45aefbec999e.metadata
    "visibleName": "gunnm_5"
/home/root/.local/share/remarkable/xochitl/545c8882-1efc-4500-b09d-cbd70e9fdb89.metadata
    "visibleName": "gunnm_6"
/home/root/.local/share/remarkable/xochitl/c5eddb4b-9f99-4d0f-bbbd-ec8752bbbc32.metadata
    "visibleName": "Knowledge mgmt"
/home/root/.local/share/remarkable/xochitl/f464e0ba-9021-4ab6-95bd-631a015133a9.metadata
    "visibleName": "The art of computer programming"
/home/root/.local/share/remarkable/xochitl/2d66256c-35df-4398-a3c3-8083d63c546a.metadata
    "visibleName": "The Rust Programming Language"
/home/root/.local/share/remarkable/xochitl/63566dae-458e-4343-b047-3b75f81fbd7f.metadata
    "visibleName": "The memory models that underlie programming languages"
/home/root/.local/share/remarkable/xochitl/d7807e58-f473-4a61-a34c-39f2c63f0c15.metadata
    "visibleName": "Red Rising 5: Dark Age"
/home/root/.local/share/remarkable/xochitl/13df9036-e63d-41fb-8861-7bb7a8383683.metadata
    "visibleName": "Chaos engineering"
/home/root/.local/share/remarkable/xochitl/3ce13086-8125-4440-aea9-c4e749963e84.metadata
    "visibleName": "Quick sheets"
/home/root/.local/share/remarkable/xochitl/5490a0fe-6e95-4e44-a674-31a9de2d3d90.metadata
    "visibleName": "The Art of Computer Programming, Volume 3: Sorting and Searching, Second Edition"
/home/root/.local/share/remarkable/xochitl/a7d1143a-ccc9-451d-8464-de6e468252a6.metadata
    "visibleName": "The Rust Programming Language"
/home/root/.local/share/remarkable/xochitl/7654cd66-bd0a-4b2d-8ea5-8fd35daba9c0.metadata
    "visibleName": "gunnm_4"
/home/root/.local/share/remarkable/xochitl/06916f31-0c7b-4572-ba26-1b27e08e13fa.metadata
    "visibleName": "gunnm_7"
/home/root/.local/share/remarkable/xochitl/04c63424-ee52-4b31-8027-e21548a764e5.metadata
    "visibleName": "gunnm_8"
/home/root/.local/share/remarkable/xochitl/39bad5e3-c0be-4f35-99de-b1388408172d.metadata
```