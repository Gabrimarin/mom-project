import stomp
import broker_gui


# Register a subscriber with ActiveMQ. This tells ActiveMQ to send
# all messages received on the topic 'topic-1' to this listener
# Act as a message publisher and send a message the queue queue-1



gui = broker_gui.BrokerGUI()
gui.mainloop()
