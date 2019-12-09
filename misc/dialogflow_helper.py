import dialogflow
import os


class DialogFlowHelper:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/key.json"
        self.project_id = "websitereader-srqsqy"

        self.contexts_client = dialogflow.ContextsClient()
        self.intents_client = dialogflow.IntentsClient()

    def createContext(self, name):
        # todo create context.
        parent = self.intents_client.project_agent_path(self.project_id)
        parameters = dialogflow.types.struct_pb2.Struct()
        parameters["prova"] = 20

        context = dialogflow.types.context_pb2.Context(
            name="projects/" + self.project_id + "/agent/sessions/-/contexts/" + name,
            lifespan_count=1,
            parameters=parameters
        )

        return


helper = DialogFlowHelper()
helper.createContext(name="open-online")
