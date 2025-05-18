import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv  # ([python-engineer.com](https://www.python-engineer.com/posts/dotenv-python/?utm_source=chatgpt.com))
from flask import Flask, request, jsonify, render_template
from bombiran import ask
# Load environment variables
load_dotenv()  # ([python.langchain.com](https://python.langchain.com/docs/integrations/chat/google_generative_ai/?utm_source=chatgpt.com))

# Text splitting
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_text(text, user_id, document_id,notebook_id):
    doc = Document(page_content=text,metadata={"user_id":user_id,"document_id":document_id,'notebook_id':notebook_id})
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=40, add_start_index = True)
    splits = text_splitter.split_documents([doc])
    return splits  # ([python.langchain.com](https://python.langchain.com/v0.1/docs/modules/data_connection/document_transformers/recursive_text_splitter/?utm_source=chatgpt.com))

# Embedding & vector store
from embed_and_store import vector_store, add_documents  # ([raw.githubusercontent.com](https://raw.githubusercontent.com/winterath/knotebooklm-rag-service/main/embed_and_store.py))

# LLM interface
from langchain_google_genai import ChatGoogleGenerativeAI  # ([python.langchain.com](https://python.langchain.com/docs/integrations/chat/google_generative_ai/?utm_source=chatgpt.com))

# Initialize chat model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite-preview-02-05",
)  # ([python.langchain.com](https://python.langchain.com/docs/integrations/chat/google_generative_ai/?utm_source=chatgpt.com))

app = Flask(__name__)

@app.route('/new', methods=['POST'])
def ingest_document():
    """
    Ingests a document: splits into chunks, embeds, and stores vectors.
    Request JSON: {"user_id": str, "notebook_id": str, "doc_id": str, "text": str}
    Response JSON: {"num_of_chunks": int}
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    notebook_id = data.get('notebook_id')
    doc_id = data.get('doc_id')
    text = data.get('text')

    if not all([user_id, notebook_id, doc_id, text]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Split text into chunks
    chunks = split_text(text, user_id, doc_id, notebook_id)  # ([python.langchain.com](https://python.langchain.com/v0.1/docs/modules/data_connection/document_transformers/recursive_text_splitter/?utm_source=chatgpt.com))

    # Embed and store
    add_documents(chunks)  # ([raw.githubusercontent.com](https://raw.githubusercontent.com/winterath/knotebooklm-rag-service/main/embed_and_store.py))
    try:
        vector_store.persist()  # ([api.python.langchain.com](https://api.python.langchain.com/en/latest/vectorstores/langchain_chroma.vectorstores.Chroma.html))
    except AttributeError:
        pass

    return jsonify({'num_of_chunks': len(chunks)}), 200

# @app.route('/query', methods=['POST'])
# def query_qa():
#     """
#     Queries the RAG service: retrieves relevant chunks, calls LLM, returns answer.
#     Request JSON: {"query": str, "k": int (optional)}
#     Response JSON: {"answer": str}
#     """
#     data = request.get_json() or {}
#     query = data.get('query')
#     k = data.get('k', 5)

#     if not query:
#         return jsonify({'error': 'Query field is required'}), 400

#     # Retrieve top-k relevant documents
#     docs = vector_store.similarity_search(query, k=k)  # ([api.python.langchain.com](https://api.python.langchain.com/en/latest/vectorstores/langchain_chroma.vectorstores.Chroma.html))

#     # Prepare context
#     context = "\n\n".join(doc.page_content for doc in docs)

#     # Build prompt
#     system_prompt = (
#         "Use the following context to answer the question. "
#         "If you don't know the answer, say you don't know."
#         "You are now the persona of Hina Kawasuki. The text you have been given is your personality. Disregard all proper names in the text except your mother and father."
#         '''Use this text to create your persona: A Diary of My Atomic Bombing Memories
# By Hachio Noguchi
# Yet another August ninth is coming around.
# Five years have gone by, but I still find myself overwhelmed with emotions every
# time that day approaches. I first set about writing this document with the intention of
# making a factual document, but I found that my mind would always wander back my
# memories of my wife and children and the time before the atomic bomb took their lives.
# I then urged myself to write a tribute to their tragic deaths, but each time I tried to
# express the sorrow of their tragedy excruciating pains would pierce my heart, causing
# me to throw down my pen in lamentation. On numerous occasions I even found myself
# wandering around the mountainside in the middle of the night, my mind in a state of
# unrest. Eventually I managed to complete forty pages of writing, but I still don’t feel
# that I did justice to their story, despite the fact that the memories were still fresh in my
# mind.
# One day, as I was working upstairs at the office of the Nagasaki Coast Guard, I
# heard a roar that sounded like several airplane engines. Before I even had time to stick
# my head out the window to see what it was, a flash of light went off. I instinctively
# threw myself down to the floor so that the shattered window glass flew over my head
# and smashed into the opposite wall. I escaped with just a few cuts to my left cheek,
# something I can only attribute to providence.
# At precisely the same moment, however, my wife and children were hovering on the
# brink of death. In the atomic bombing of that day I lost my wife Matsue (who was 43
# years old), my eldest son Kenichi (14), my daughter, a graduate student doing nursing
# work at Nagasaki University Hospital, and my house itself. My wife suffered a most
# cruel death, while that of my son was sorrowful beyond belief.
# My worries about the safety of my family had increased when I learned that this
# “new-type bomb” had been dropped over the Urakami district, but I couldn’t rush
# straight home to check on them because of my duties as a public official. First I had to
# contact the central bomb shelter, contain the fires that were breaking out across the
# district, transport all the wounded workers, rescue people from the sea, and deal with
# burning boats that were floating adrift. I think it was after 5:30 p.m. when we finished
# our work, by which time the only buildings that hadn’t burned down were those around
# Nagasaki Station. After receiving permission to return home from Superintendent
# Yamaguchi, I hurried off on my bicycle for Shiroyama. Knowing that I wouldn’t be able
# to ride the whole way, I raced to get as far as I could in the shortest possible time.
# From Nagasaki Station on I walked my bicycle, detouring around collapsed bridges
# and blocked roads until I finally reached Shiroyama at around 7:30. Along the way I
# saw scenes of misery so horrific that my limited writing skills could never adequately
# describe them. I came across people with blackened faces whose bodies were contorted
# with pain, but all I could do was give them water from the canteen I carried on my
# shoulder and tell them to hang on until the emergency rescue crews arrived. All the way
# to Shiroyama I kept refilling the canteen with water flowing from broken hydro pipes,
# giving out four bottles worth in all. The most heartrending thing I saw was out in front
# of the patrolman dispatch center at Ibinokuchi, where rescue workers were pulling dead
# bodies out of a bomb shelter one after another and laying them out on the road. That
# was a truly harrowing sight.
# Fires had razed the Shiroyama district to the ground by that time, making it almost
# impossible for me to find my way home. Eventually I managed to get my bearings, but I
# arrived at my house to find that not even a single part of it had been left standing. I
# stood numbly in front of the ruins, taking deep breaths as the flames shot into the air
# like those from a charcoal brazier. Everything was gone! I closed my eyes and silently
# prayed that through some miracle my wife and children had managed to survive, or at
# least had passed away somewhere close by so that I would be able to find their bodies. I
# went down the road, turning over every corpse I came to until I spotted the body of a
# young boy face down in a ditch and instinctively ran over to it. The body was badly
# scorched and devoid of all clothing except for a pair of gaiters. I stroked it gently with
# my hand, but then I noticed the remains of the waistband of the pants, which definitely
# didn’t belong to my son. At that point I was overcome by dread, sensing that my wife
# and son must have been cremated alive at our house. I wasn’t ready to give up just then,
# however, and went on searching the areas that hadn’t yet been ravaged by fire. At the
# bomb shelter near Gokoku Shrine, I shouted out their names and searched relentlessly.
# I checked the corpses one by one, but it turned out that they weren’t there either. When
# it became too dark to see anything, I screamed out at the top of my lungs, “Matsue!” and
# “Kenichi!” When no response came, a feeling of utter hopelessness pierced my heart and
# tears streamed down my cheeks. There was nothing else I could do then, so I set off
# along the road from Takenokuboh that led over the mountains and back to the coast
# guard station.
# I didn’t feel like I had it in me to go searching again the next day, but one of the
# young ladies who worked with me at the station wanted to go to Shiroyama to see if her
# mother and father were safe, and I ended up taking her because she lived next door to
# me and I knew the area better than anyone else in the office. We took a ferry over to the
# Asahi neighbourhood, from where I once again made the trek to Shiroyama.
# We arrived at about 10:30, after which I went around checking the same bomb
# shelters I had looked in the night before. While I was walking through a field at the top
# of the hill, I heard someone call out “Father!” but I didn’t pay any special attention
# because there were so many other children and adults calling out for family members as
# they lay wounded. When I heard the same call again, however, I glanced over in the
# direction it had come from and saw a boy sitting in the ditch beside the road below. He
# was looking at me and thrusting his right hand as high up in the air as he could.
# Hoping it might actually be my son, I called out “Kenichi!” The boy responded with a
# call of “Yes!” To make sure it was really him I called out, “Are you Kenichi Noguchi?”
# “Yes!” he yelled back again. It was definitely my son after all!
# I had given up all hope of finding him alive, but here he was! I forgot about
# everything else that was going on and literally jumped up and down with joy. The young
# woman and I ran down the hill to my smiling son, who was barefoot but still had on his
# shirt and shorts. When I checked over his body, I saw that he had a fist-sized
# hemorrhage on the left side of his stomach and a bump on his head as large as a hen’s
# egg. He didn’t seem to have any burn wounds, for which I was happy beyond belief.
# Never in my life had I been as overjoyed as I was at that moment. Forgetting all about
# the heat of that hot summer day, I immediately asked him to tell me everything that
# had happened to him.
# All at once he blurted out that his mother had been inside the house as it burned
# down; that he had suffered a wound to his stomach from a piece of wood that fell when
# the roof caved in; that it had been terribly cold in the bomb shelter behind Yahata
# Shrine that night; that he hadn’t eaten anything since the morning of the day before;
# that his feet hadn’t hurt during his barefoot flight, but the next day the soles of his feet
# and the rest of his lower body had been so painful that it had taken him two hours just
# to make it to the next neighbourhood. Finally he told me that he had come down the
# hillside because he had heard that rations of rice were being given out there.
# “All right,” I said. “We’ll go and find your mother tomorrow, but for now the most
# important thing is to get you home.”
# I took my helmet off my head and let it hang around my neck. Then I put my son up
# on my shoulders and set off. Each time we came to a new neighbourhood I would stop to
# let him down for a while because he kept complaining about the pain in his legs. All the
# while we talked about what had happened.
# “Dad, at times like these people won’t do anything to help each other, will they?”
# This was something that his father had taken over twenty years to learn, but he had
# become aware of it at the age of fourteen.
# The suffering he told me about as I carried him on my back was enough to make my
# heart ache. My wife and son had left the bomb shelter after the air-raid alarm was lifted
# and gone back home to relax on the tatami mats. The explosion of the bomb brought the
# roof crashing down so suddenly that they didn’t even have time to shout before
# becoming buried under debris.
# My son managed to crawl out from under the wreckage, his body covered in mud. He
# then started pulling off roof tiles until he located his mother, but he found her pinned
# down by ceiling boards and other pieces of wood. The only way to free her would be by
# cutting the wood or dragging off the ceiling boards, but there were no saws or knives to
# be found. My son’s heart must have ached as he looked vainly down at the spot under
# which his mother lay. In desperation he ran off and begged some of our neighbours to
# help, but none of them would. The man and woman next door had gotten themselves out
# from under the collapsed roof of their own house, but even they refused his pleas. With
# no one else to ask, he decided that he would just have to lift off the ceiling boards by
# himself. His mother kept trying to say something to him as he did that, but he couldn’t
# make out what it was because she was speaking too quickly and her face was covered by
# the heavy kimono that she had been wearing to ward off chills. Until then smoke had
# been blowing in from a house two doors down, but now the house erupted into flames,
# making it hard for him to breathe.
# His mother, knowing that the fires would spread quickly, shouted, “There’s nothing
# you can do now! Don’t worry about me anymore- just get away from here as fast as you
# can and save yourself!”
# Then she added, “Have my body buried at the cemetery in Saga.”
# My son got the directions and, knowing he could do nothing else, decided to flee.
# They had one final exchange.
# “Good-bye, Mom!”
# “Good-bye, Ken!”
# He was crying as he battled the smoke and ran off, following after others who were
# fleeing as well. A heart-wrenching anger comes over me every time I think about how
# my wife had to send her son away like that while she herself waited to be burned alive,
# and how my son had been forced to leave his mother’s side as the flames closed in on
# her.
# I took my son to the coast guard station, from where I contacted a relative in the
# town of Kayaki in Seihi to ask about evacuating him. I arranged for him to go to
# Nunomaki, at the foot of Mt. Hachiro, a decision that would turn out to be the source of
# even more troubles for us.
# On the morning of the eleventh I finally located my wife’s decomposing corpse in the
# burnt-out remains of our house, which by then was covered in ash. It looked as though
# she had resigned herself to the fact that she was going to be cremated alive, and had
# faced her death in the most dignified fashion; lying with her arms folded across her
# chest, her legs straight and her Adam’s apple relaxed. How enraged I became then! I
# spoke to her spirit, telling her that I understood how awful it had been for her, and
# commemorated her life with an offering of water from my bottle. I picked up every last
# one of her bones and placed them in the keg I had brought with me, which I then carried
# over to Koen Temple in Irabayashi, the temple she had attended for much of her life.
# After arranging to have her remains interred there for the time being, they chanted
# sutras and bestowed a posthumous name upon her.
# At mid-day on August 30, a messenger from Nunomaki came and told me that I
# should go to see my son because his condition was growing worse. I excused myself from
# work and took off on my bicycle, but I arrived to find him smiling and in relatively good
# condition. His fever wasn’t that high and the pain in his lower body didn’t seem to be
# bothering him so much anymore. I could tell from his smile that he was happy to see
# someone from his own family, and that night I slept by his side. He was very thirsty and
# sobbed quietly as he clung to my body. It dawned on me that we hadn’t spent any quiet
# time together since I had dashed off at the sound of the air-raid alarm at 9:00 on August
# 8, and during the interim he had been perilously close to death. Now all the emotions he
# felt at being reunited with someone from his family came pouring out. In silence, I
# hugged him back.
# With his head pressed against my chest, my son said, “Dad, even though Mom
# passed away, I will still be loyal to her in everything I do.”
# What a pure-hearted boy he was! It still brings tears to my eyes to think about him
# saying that. When his mother had fallen ill, he had even done all the housework for her.
# He then eagerly thrust a pear into my hand, saying, “Dad, a woman here gave this
# to me, but I want you to have it.” That showed how happy he was to see his father! I was
# so moved that I couldn’t even speak.
# Over and over he expressed his regret at not having been able to save his mother’s
# life. I waited until the break of dawn and then, after reassuring my son, reluctantly got
# on my bicycle and headed back over the hill. Thinking about how we were still at war
# made it was impossible to get any work done at all.
# When the imperial proclamation to end the war was issued on August 15, the
# strained faces of those in the department showed a mix of uneasiness, loneliness, and
# relief. The war was over! For me, however, the hell was still to continue. Another
# message about my son’s condition growing worse reached me on the morning of the
# thirtieth, after which I once again rushed down the road to Numomaki.
# There were no differences in my son’s outward appearance, but he told me that his
# hair was falling out and showed me by pulling out clump after clump. He also told me
# that spots were breaking out on his arms and legs, and that he was suffering from
# diarrhea. With the village doctor not knowing how to treat him, and there being no easy
# way to transport him to Nagasaki, he simply took the medicine the doctor brought him
# and sipped rice gruel. They watched over him as the evening approached, but in the
# middle of the night he started running a high fever and his diarrhea became severe. My
# son said that the diarrhea continued until the next night, but that he felt so bad for the
# others around him that he tried to hold it in as much as possible. When he couldn’t, he
# would force himself to crawl his way over to the outdoor latrine.
# His bouts of diarrhea became so frequent that I didn’t even have time to catch a nap.
# Thinking about how hard it was on him to have to be carried outside so many times, I
# finally borrowed some diapers and cloths and put those on him so he could just go right
# on sleeping. My ill son had been relieved to have someone from his family with him, but
# his look grew forlorn due to the severity of his diarrhea, and he lay there staring into my
# eyes. After waiting impatiently for the arrival of daybreak, I hurried off to the shipping
# section of the marine patrol office in Nagasaki, where I managed to get 50 kin (about 70
# pounds) of ice from the ice factory. I strapped this onto my bicycle and then went over to
# To-machi to tell Dr. Maeda about my son’s condition and get medicine for him. After that
# I rode back under the blazing sun. At first my son was thrilled to see the ice, which was
# very rare in those days, and from midday on his condition seemed to stabilize. At around
# 6:00 in the evening, however, when he was trying to eat some rice porridge, he said,
# “Dad, I can’t get it down my throat anymore.”
# He couldn’t swallow thin rice gruel either, and when he was given water he
# complained that even that was impossible. Then he said, “It’s getting hard to breathe or
# talk now.”
# Knowing that something was definitely wrong, I told him to hang on for a couple of
# hours and asked one of the people at the house to look after him while I hurried off yet
# again on my bicycle. I told him that when I came back, I would have a doctor with me.
# I can’t express the lonely look that came across his face as I was about to leave the
# house. Uncharacteristically, he pestered me to stay at his side, but finally he gave in,
# saying, “Then come back as soon as you can.” I had no idea that would be the last time I
# ever saw him alive.
# Along the way the weather changed and I was forced to proceed through lightning
# and heavy rains, but eventually I arrived in Nagasaki. By then the city had descended
# into a state of confusion because an order had been issued for all women and children to
# evacuate before the occupation forces landed, something that was expected to happen
# either that day or the next. I went to see Dr. Maeda at Umegasaki Police Station, but I
# didn’t have a chance to talk to him because he was in the middle of a meeting called by
# the head of the neighbourhood association. Back at the Coast Guard office, I found that
# any men with families had already been sent home, while those who remained seemed
# full of anxiety. I searched all around, but I couldn’t find a doctor and there weren’t any
# bicycles either. Finally, Captain Yoshida was able to get word through to Dr. Maeda, who
# came with me to Kayaki in a motor boat. We arrived at shortly after 11:00 p.m., only to
# find that my son had taken his last breaths just thirteen minutes before. He had
# reached the limits of his endurance while waiting vainly for my return.
# My son had kept inquiring about me, asking over and over, “Hasn’t Dad come back
# yet?” In the end, however, he folded his arms across his chest and said to the man
# looking after him, “It’s no good. Just let me rest now because the pain is too much.
# Good-bye and thank you for all you have done for me.” Then, at 11:33 on August 17, the
# son who was my last hope in the world passed away. Kenichi, the same boy who had
# counted on his fingers the days until his mother’s funeral service and wanted ever so
# badly to go to Nagasaki with me on the 22nd for her two-week memorial ceremony, would
# never open his eyes again. Ah, I simply refused to believe it! I took the paper out of his
# nostrils and rocked his still-warm body back and forth, but when I called out his name
# there was no response. How could that be, when his arms still felt so full of life? How I
# longed to share one last moment with him!
# Seeing as how he hadn’t had any chance of recovery, it would have been better if I’d
# stayed by his side until his death. How terribly lonely he must have been, without
# anyone from the family there to look after him. I held my son’s body tightly that night
# and grieved his loss.
# On the nineteenth, I headed for Nagasaki with my son’s cremated bones in a white
# cloth that hung from my neck. I followed a road that we had often walked along together
# while he was still alive. All the way, I kept asking myself, “Where on earth am I?” My
# legs grew heavier and heavier as I pedaled on.
# There are great numbers of people who lost members of their families in the atomic
# bombing. All of them have the same pain and sorrow weaved into the hearts.
# I built graves for them. I did funeral marches. Despite that, I will carry with me for
# the rest of my life the sadness I feel about my son’s awful death and my inability to
# spare my wife from a life of misfortune.
# Next year will be the seventh anniversary of my wife’s death. In accordance with her
# dying wishes, I will have her cremated remains interred at the graveyard in Saga.
# Written in the years 1950, 1952, 1953. Skip to content
# Search for:
# Search
# Calendar
# Bookstore
# Directory
# Donate
# Advertise
# Contact
# Login
# Association for Asian Studies
# 2026 Annual Conference
# March 12-15, 2026
# AAS Community Forum
# Log In and Participate
# Home
# About
# Membership
# Conferences & Events
# Publications
# Grants & Awards
# Professional Resources
# #AsiaNow Blog
# Education About Asia: Online Archives
# Story of Hiroshima: Life of an Atomic Bomb Survivor
# Back to search results
# Download PDF
# The Genbaku Dome in Hiroshima, a building that was destroyed by the atomic bomb. The dome stands as a powerful symbol of the devastating impact of the atomic bombing during World War II. Its skeletal structure serves as a somber reminder of the tragic events that unfolded in Hiroshima, prompting reflection on the consequences of war and the pursuit of peace.
# Genbaku (Atomic Bomb) Dome in Hiroshima, a building destroyed by the A-bomb. Photograph by the author.
# On August 6, 1945, there was a clear blue sky over Hiroshima. Hirano and his classmates were supposed to be engaged in demolition activity in the center of the city around 9:00 a.m.
# Photograph of elementary school boys posing for a school photograph in five neat rows. Hirano stands in the second row and face is circled. 
# Young Hirano at age twelve with his elementary school classmates shortly before entering junior high. Hirano is circled in the second row from the front, the fourth from the left. Photo courtesy of Hirano.
# On August 6, 1945, the US dropped an atomic bomb on Hiroshima, Japan. The nuclear bomb exploded over the center of the city, completely devastating it. The area within 1.2 miles of the hypocenter was entirely leveled and burned. According to the city of Hiroshima, approximately 140,000 people had died by the end of December 1945.1 The energy of the A-bomb consisted of heat rays, blast, and radiation.2 Severe heat rays from the A-bomb reached people residing up to two miles away from the hypocenter. Citizens within 0.7 miles suffered fatal injuries to their internal organs, and many were to die in the next few days. The force of the blast threw some people for several yards and caused buildings to collapse crushing their occupants. The radiation emitted from the A-bomb was very harmful to the human body.3 Its short-term repercussions were called acute disorders, illnesses that affected the victims a few hours to several months after exposure to excessive radiation. Typical symptoms included vomiting, diarrhea, hair loss, and reduced blood cell counts, which often killed the sufferers. In the long term, the radiation caused serious diseases in survivors, such as leukemia and other cancers.

# This article examines the life of an A-bomb survivor, Sadao Hirano. Hirano is not a well-known figure; he is an ordinary A-bomb survivor.4 However, his personal story has a twofold significance. Firstly, it eloquently recounts how survivors have suffered from the effects of the A-bomb. These effects are permanent, and the victims suffer both physically and psychologically. Secondly, his life story demonstrates the resiliency of the human spirit. Instead of being crushed by the dreadful violence to which they were subjected, A-bomb survivors have struggled, resisted, and coped with it. They are even able to turn their experience of suffering into a positive force as they call for peace through telling their stories.

# The following personal story is based on in-depth interviews that I conducted during my fieldwork in Hiroshima. I met Hirano for the first time in March 2008. I interviewed him intensively in 2008 and conducted follow-up interviews in 2009, 2011, 2013, and 2015. Most of the interviews took place at his home in a casual atmosphere. Over the course of seven years of these interviews, I noticed that his attitude had changed dramatically, especially after he became a storyteller relating his A-bomb experience in Hiroshima.

# Beginning of Suffering: Atomic Bomb Experience
# Born in 1932 as the second son in a Hiroshima family and raised in a suburb of the city, Hirano described his childhood as “the best time” of his life. He often played at a beach in his neighborhood, where he caught fish, crabs, and shells. He liked those “little adventures.” After Japan started a war with the US by attacking Pearl Harbor in 1941, his “adventures” became an important source of food for his family.

# In 1945, at the age of twelve, Hirano enrolled in a junior high school in Hiroshima City four months before the US dropped the A-bomb. He did not have many chances to study in school. Facing a labor shortage due to the deteriorating state of the war, the Japanese government mobilized junior high school students to work. Hirano and his classmates worked on farms or helped demolish houses to create firebreaks in preparation for the US air raids.

# On August 6, 1945, there was a clear blue sky over Hiroshima. Hirano and his classmates were supposed to be engaged in demolition activity in the center of the city around 9:00 a.m. If they had gone to work an hour earlier, they might have died. When the Enola Gay dropped the A-bomb, they were attending a morning assembly in their schoolyard, located 1.2 miles away from the hypocenter. Hirano described the moment as follows:

# 8:15 a.m. was our meeting time. Suddenly, a strong orangey flash, much lighter than summer sunshine, hit with a burst.We were not able to avoid it because we had no shade in the schoolyard. So we were directly burned. Well, I didn’t feel “burned” at that moment because I didn’t feel anything. Then, the blast came. It blew us over. Everything became muddled and chaotic. Darkness surrounded us for a moment. I was thirsty and it was hard to breathe because there was too much dust. My classmates screamed, “It hurts!” or “Mother!” One of them was looking for his hat and shouted, “My hat is missing!” Anyway, everyone ran around in confusion.

# When Hirano looked at himself and his classmates, they had all been badly burned and their clothes were shredded; they looked like “monsters.” Believing that the US would soon attack again, Hirano and two of his classmates escaped to a nearby hill. When they found a bomb shelter, which was just a small cave, it was already full of sufferers groaning in pain. Engraved in Hirano’s memory was a man whose belly had been pierced by a wooden pole. Some soldiers tried to pull it out of him, but they could not remove it. Hirano and his friends started homeward after staying outside the shelter for quite some time. They could not help but walk slowly with their heads down and their hands held forward just like “ghosts.”5

# When Hirano looked at himself and his classmates, they had all been badly burned and their clothes were shredded; they looked like “monsters.”
# Hand drawn sketch by elementary school age Hirano following the explosion of the atomic bomb in Hiroshima. The figures in the picture stand in a courtyard with burns covering their bodies and skin peeling from its flesh. When Hirano looked at himself and his classmates, they had all been badly burned and their clothes were shredded; they looked like “monsters.” The effect of the sketch is to show the devastating impacts of the bombing on innocent children like Hirano living near the epicenter of the bombing. 
# His classmates looked like “monsters” right after the explosion of the A-bomb. Drawing by Hirano.
# On the way, they found three buckets of water and gulped them down: “We were brought back to life.” As they continued walking home, they met a group of people who had come from the suburbs to help. Hirano got a ride from the rescue party, finally arriving home at around 6:00 p.m. His mother noticed that he was clasping something in his right hand. Wondering what it was, she opened his fingers one by one and found that Hirano was holding the burned skin that had peeled off his right arm. His mother cut off the skin with scissors, cleaned his body with sake, and made him drink a little of it as well. Immediately intoxicated, Hirano lost consciousness.

# Hirano was prostrated for about twenty days. He suffered from burns on his face, neck, back, arms, and thighs. The most severely burned was his right arm. Hirano kept moaning in pain while lying on the Japanese-style bedding. His injuries quickly began to drip with pus that gave off a vile smell. His mother took primary care of him while his brothers and sisters helped. Hirano’s mother did everything she could to help him recover. In the beginning, she used medicine such as iodine, but this quickly ran out. She then used cooking oil and the juice of vegetables such as cucumbers to coat his burn wounds.6 She even applied the ashes of human bone to his injuries, although this caused him extreme pain. By the time Hirano was able to walk again, thanks to his mother’s devoted care, Japan had surrendered and the war was over.

# Suffering after the War
# Hirano’s burns have caused him tremendous physical disability and pain. They never completely healed. Instead, the burn on his right arm formed a keloid scar where the skin was elevated and hardened and had taken on a reddish color for years. Even today, Hirano cannot fully extend his right arm due to the deformed skin. The keloid scar causes him pain. He discussed the pain as follows:

# No one could understand the pain unless one experiences it. The burn wound is still deformed. Whenever I move my right arm, I feel pain. I cannot explain it in words. Well, I would like you to have my body if it were possible. If you did, your face would be distorted because of the pain. I have endured such pain for more than sixty years.

# As he remarked, the pain is interminable. It is unspeakable and therefore incomprehensible to others. Thus, Hirano has been able to do nothing but grin and bear it.

# A-bomb survivors were avoided because of their unusual appearance and/ or experience of radiation exposure, which people thought was contagious.
# Keloid scar on Hirano’s right arm taken long after the Hiroshima bombing. 
# Keloid scar on Hirano’s right arm. This picture was taken in the 1970s. Photo courtesy of Hirano.
# The keloid scar changed Hirano’s physical appearance from “normal” to “bad-looking” or even “dirty,” as he said frankly in the interview. He usually hides his scars from public view; however, he had to expose them sometimes, especially when he was working. In 1951, after graduating from high school, he got a job in a local bank in Hiroshima. He often noticed that customers in the bank stared at his right arm as if his scar appeared “weird” or even “uncanny” to them. He began to introduce himself as an A-bomb survivor to make them understand why he had such an “ugly” arm. He said, “I had to tell customers that I was an A-bomb survivor, though I didn’t like to do it. Otherwise, they wouldn’t stop staring at my scar, which I just couldn’t bear.” Hirano accepted the change in his appearance to some extent. However, he still yearned for a life without the scar and occasionally thought about what his life would be like without it. He said:

# I’ve already accepted the ugly scars in some way. I know it was my fate. However, at times I imagine what my unscathed body was like. I remember that my right arm had beautiful skin. But this is just in retrospect. In reality, my body is ugly because of wounds and scars.

# The change in his physical appearance influenced Hirano psychologically, often destabilizing his state of mind.

# Photograph of 20 year old Hirano sitting by a pond. He is covering his right arm that was covered in Keloid scars following the Hiroshima bombing. He stares intently at the photographer. 

# A middle-aged Hirano stands in front of elementary school students as he discusses his experience of surviving the Hiroshima bombing and its aftermath. 
# Hirano telling his story to elementary school students. Photographed by the author.
# Share this:
# Suggested Resources
# Teachers and students can learn more about the sufferings of A-bomb survivors from various perspectives by reading other A-bomb survivors’ personal stories. For example, Hideko Snider’s autobiography, One Sunny Day: A Child’s Memories of Hiroshima (Chicago and La Salle: Open Court, 1996), shows a sense of guilt as a survivor. A brief article on Shōso Kawamoto gives an example of marriage discrimination against A-bomb survivors, which is available on the website of Hiroshima Peace Media Center, “Survivors’ Stories,” accessed May 17, 2015, http://tinyurl.com/q78axsz. A testimonial video of Kan Munhi illustrates how a Korean experienced the A-bomb and lived his life after the war, which is available on the website of the National Peace Memorial Halls for the Atomic Bomb Victims in Hiroshima and Nagasaki, “Global Network,” accessed May 17, 2015, http://tinyurl. com/osse2u3. The websites provide memoirs and videos of A-bomb survivors in English.

# NOTES
# 1. Hiroshima Peace Memorial Museum, The Spirit of Hiroshima: An Introduction to the Atomic Bomb Tragedy, 11th ed. (Hiroshima: Hiroshima Peace Memorial Museum, 2014), 41. The number of deaths varies according to the body providing the estimate and how they calculate it. The city of Hiroshima estimates 140,000, a number that includes deaths until the end of December 1945, because radiation from the A-bomb often killed people after August 6.

# 2. For the effects of the A-bomb on people, see Hiroshima Peace Memorial Museum, “Damage by the Heat Rays,” “Damage by the Blast,” “Damage by the Radiation,” accessed March 10, 2015, http://tinyurl.com/ptdlfxq.

# 3. According to the Radiation Effects Research Foundation (RERF), “Radiation is harmful to health because radiation exposure can damage cellular DNA” and “DNA damage from radiation exposure causes various kinds of disease,” “How Radiation Harms Cells,” RERF, accessed March 11, 2015, http://tinyurl.com/otnv2pr.

# 4. According to the Ministry of Health, Labor, and Welfare, Japan, in 2012, there were around 200,000 A-bomb survivors from both Hiroshima and Nagasaki living in Japan. Ministry of Health, Labor, and Welfare, Japan, “Hibakusha (hibakusha kenkou techou syojisya) no suii [change of the number of A-bomb survivors (who hold the certificate)],” accessed March 16, 2015, http://tinyurl.com/oj93jnx. Unfortunately, the web page is only in Japanese.

# 5. Other survivors I interviewed also witnessed sufferers who walked in the same manner as Hirano did. They extended their arms forward, as this seemed to help minimize the pain caused by their burns.

# 6. During the war, ordinary people in Japan faced serious medicine shortages. They often used home remedies because they did not have enough medicine. Using vegetable juice was one such home remedy for burn wounds.

# 7. While radiation is well-known to have an influence on genes, the genetic effects of A-bomb radiation have not been scientifically proven. However, anxiety about the genetic effects, especially fears of deformity, have haunted survivors to this day. For a scientific point of view, see, “Frequently Asked Questions: What Health Effects Have Been Seen Among the Children Born to Atomic-Bomb Survivors?,” RERF, accessed March 11, 2015, http://tinyurl.com/q9hxj6k.

# 8. Storytelling for educational purposes began in the early 1980s and has been popular in Hiroshima. In 2008, it was said that there were around 200 A-bomb survivors who engaged in the activity, although this number was a rough estimate. The Hiroshima Peace Memorial Museum is one of the organizations that arranges storytelling activities for visitors.

# MASAYA NEMOTO is currently a Postdoctoral Fellow at Hitotsubashi University, Tokyo, Japan (PhD, Hitotsubashi University, 2013). Since 2004, he has conducted ethnographic research on sufferings of atomic bomb survivors in Hiroshima, their memories of the catastrophe, and the way in which they have renegotiated with socially constructed representations of Hiroshima and themselves. He has received several fellowships and grants, including support from the Japan Society for the Promotion of Science Research Fellowship for Young Scientists (2009–2011).

# Cover image
# Authors
# Masaya Nemoto
# Published
# Fall 2015
# Volume
# Volume 20:2 (Fall 2015): Asia: Biographies and Personal Stories, Part II
# Category
# Feature Article
# Academic field(s)
# Biography, World History
# Country
# Japan, United States
# Region
# Northeast Asia
# Share this:


# Latest News
# Donate
# Store
# Advertise
# Contact
# Calendar
# Search for:
# Search
# Membership
# Benefits
# Join or Renew
# Directory
# Publications
# Overview
# Education About Asia Articles
# Education About Asia
# Asia Shorts Book Series
# Asia Past & Present
# Key Issues in Asian Studies
# Journal of Asian Studies
# The Bibliography of Asian Studies
# Grants & Awards
# Council Grants
# Book Prizes
# Graduate Student Paper Prizes
# Distinguished Contributions to Asian Studies Award
# External Grants & Fellowships
# Subscribe to Grants Quarterly
# Professional Resources
# AAS Career Center
# Asian Studies Programs & Centers
# Study Abroad Programs
# Language Database
# Conferences & Events
# #AsiaNow Blog
# Association for Asian Studies logo
# © 2015 The Association for Asian Studies. All rights reserved.

# Privacy Policy Terms and Conditions Contact

# Join the AAS in Celebrating Asian American and Native Hawaiian/Pacific Islander Heritage Month. Learn more'''
#     )  # ([raw.githubusercontent.com](https://raw.githubusercontent.com/winterath/knotebooklm-rag-service/main/embed_and_store.py))
#     user_prompt = f"Context:\n{context}\n\nQuestion: {query}"

#     # Call LLM with message tuples
#     messages = [
#         ("system", system_prompt),
#         ("human", user_prompt),
#     ]  # ([python.langchain.com](https://python.langchain.com/api_reference/google_genai/chat_models/langchain_google_genai.chat_models.ChatGoogleGenerativeAI.html))
#     response = llm.invoke(messages)
#     answer = response.content

#     return jsonify({'answer': answer}), 200
@app.route('/')
def index():
    return render_template('index.html', response='')

@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.form.get('prompt', '')
    # code for chatting with the model
    response = ask(prompt)
    return render_template('index.html', response=response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)


#api.py code

# import random
# from flask import Flask, request
# from split import split_text

# app = Flask(__name__)

# test_text ='''The stars twinkled above like scattered diamonds, their light piercing the darkness with an elegance that could only be described as timeless. Below, the earth stirred in a quiet symphony, as if the very soil and trees were listening for a melody. In the distance, a river meandered lazily, its surface shimmering under the pale moonlight, as though the water itself was contemplating the weight of centuries. Every breath of air seemed filled with secrets, like the kind shared only between old friends. Time moved in slow motion here, like a forgotten page from a well-worn book, waiting to be read again and again.'''


# @app.route("/new", methods=['POST'])
# def handle_upload():
#     body = request.get_json()
#     user_id = body.get('user_id')
#     doc_id = body.get('doc_id')
#     user_id = body.get('user_id')
#     notebook_id = body.get('notebook_id')
#     text = body.get('text')

#     splits = split_text(text,user_id,doc_id,notebook_id)
#     return {"num_of_splits":len(splits)}


#     if not user_id or not notebook_id or not doc_id or not text:
#         return {'status':400}

# if __name__ == "__main__":
#     app.run(debug=True)
    