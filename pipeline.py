from agents import create_search_agent,create_reader_agent,writer_chain,critic_chain

def run_pipeline(topic:str) -> dict:
    state_memory = {}
    print()

    #invoking search agent
    print("----Search agent is working ----")
    print()
    search_agent = create_search_agent()
    search_results = search_agent.invoke({
        "messages":[{
            "role":"user",
            "content":f"Research the following topic and use the web_search tool: {topic}"
        }]
    })
    state_memory["search_results"] = search_results["messages"][-1].content
    print("\nSearch results\n",state_memory["search_results"])

    #Reader agent
    print()
    print("----Reader Agent is working ----")
    print()
    reader_agent = create_reader_agent()
    reader_results = reader_agent.invoke({
        "messages":[{
            "role":"user",
            "content":f"""

            Based on the following search results about '{topic}',

            pick the 2 most relevant URL and scrape it for deeper content.\n\n

            Search Results:\n{state_memory['search_results'][:800]}

            """
        }]
    })
    state_memory["reader_results"]=reader_results["messages"][-1].content
    print("\nReader results\n ",state_memory['reader_results'])

    #Writer Chain
    print()
    print("----Writer chain is working----")
    print()
    research_combined = f"Search Results - \n{state_memory['search_results']}\nScrapped Results(detailed) - \n{state_memory['reader_results']}"
    state_memory["report"] = writer_chain.invoke({
        "topic":topic,
        "research":research_combined
    })

    print(f"\nFinal Report - \n{state_memory['report']}")

    #Critic chain
    print()
    print("Critic chain is working..")
    print()
    state_memory["feedback"] = critic_chain.invoke({
        "topic":topic,
        "report":state_memory["report"]
    })
    print(f"\nFeedback - \n{state_memory['feedback']}")

    return state_memory


#Calling function
if __name__ =="__main__":
    topic = input("\nEnter a research topic :- ")
    run_pipeline(topic)


