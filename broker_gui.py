import tkinter as tk
import random
import stomp

host = [('broker.hivemq.com', 1883)]

class Listener(stomp.ConnectionListener):
    def __init__(self, handle_message):
        super().__init__()
        self.handle_message = handle_message

    def on_connected(self, frame):
        print('connected to ActiveMQ')
        print('frame: ', frame)

    def on_error(self, frame):
        print('received an error "%s"' % frame)

    def on_message(self, frame):
        self.handle_message(frame)


class ClientGUI(tk.Toplevel):
    def __init__(self, master = None, id=None, on_message=None, check_topic=None, check_queue=None):
        super().__init__(master=master)
        self.title("MOM Client")
        self.geometry("")
        self.id = id
        self.show_main_screen()
        conn = stomp.Connection()
        self.conn = conn
        conn.set_listener('', Listener(
            lambda frame: self.append_message(frame)
        ))
        conn.connect('admin', 'admin', wait=True, host=host)
        self.on_message = on_message
        self.check_topic = check_topic
        self.check_queue = check_queue

    def subscribe_topic(self, topic_name):
        if self.check_topic(topic_name):
            self.conn.subscribe(destination=f"/topic/{topic_name}", id=self.id, ack="auto")
            try:
                self.error_label.destroy()
            except:
                pass
            self.error_label = tk.Label(self, text="Subscribed", fg="green")
            self.error_label.grid(row=6, column=0)
        else:
            self.error_label = tk.Label(self, text="Topic does not exist", fg="red")
            self.error_label.grid(row=6, column=0)
    def subscribe_queue(self, queue_name):
        if self.check_queue(queue_name):
            self.conn.subscribe(destination=f"/queue/{queue_name}", id=self.id, ack="auto")
            try:
                self.error_label.destroy()
            except:
                pass
            self.error_label = tk.Label(self, text="Subscribed", fg="green")
            self.error_label.grid(row=6, column=0)
        else:
            self.error_label = tk.Label(self, text="Queue does not exist", fg="red")
            self.error_label.grid(row=6, column=0)
    def send_message_topic(self, topic_name, message):
        if self.check_topic(topic_name):
            self.on_message(f"/topic/{topic_name}")
            self.conn.send(destination=f"/topic/{topic_name}", body=message)
            try:
                self.error_label.destroy()
            except:
                pass
            self.error_label = tk.Label(self, text="Sent", fg="green")
            self.error_label.grid(row=6, column=0)
        else:
            self.error_label = tk.Label(self, text="Topic does not exist", fg="red")
            self.error_label.grid(row=6, column=0)
    def send_message_queue(self, queue_name, message):
        if self.check_queue(queue_name):
            self.on_message(f"/queue/{queue_name}")
            self.conn.send(destination=f"/queue/{queue_name}", body=message)
            try:
                self.error_label.destroy()
            except:
                pass
            self.error_label = tk.Label(self, text="Sent", fg="green")
            self.error_label.grid(row=6, column=0)
        else:
            self.error_label = tk.Label(self, text="Queue does not exist", fg="red")
            self.error_label.grid(row=6, column=0)

    def append_message(self, frame):
        destination = frame.headers['destination']
        if destination.startswith('/queue/'):
            self.queue_log.insert(tk.END, f"{destination[7:]}: {frame.body}\n")
        elif destination.startswith('/topic/'):
            self.topic_log.insert(tk.END, f"{destination[7:]}: {frame.body}\n")

    def show_main_screen(self):
        tk.Label(self, text="Topic").grid(row=0, column=0)
        self.topic_entry = tk.Entry(self, width=30)
        self.topic_entry.grid(row=1, column=0, pady=5)
        tk.Button(self, text="Subscribe", command=lambda: self.subscribe_topic(self.topic_entry.get()), width=10).grid(row=1, column=1)
        tk.Label(self, text="Message").grid(row=2, column=0)
        self.message_topic_entry = tk.Entry(self, width=30)
        self.message_topic_entry.grid(row=3, column=0,  pady=5)
        tk.Button(self, text="Send", command=lambda: self.send_message_topic(self.topic_entry.get(), self.message_topic_entry.get()), width=10, fg="blue").grid(row=3, column=1)
        self.topic_log = tk.Text(self, width=30, height=10)
        self.topic_log.grid(row=5, column=0,  pady=5)

        tk.Label(self, text="Queue").grid(row=0, column=2)
        self.queue_entry = tk.Entry(self, width=30)
        self.queue_entry.grid(row=1, column=2,  pady=5)
        tk.Button(self, text="Subscribe", command=lambda: self.subscribe_queue(self.queue_entry.get()), width=10).grid(row=1, column=3)
        tk.Label(self, text="Message").grid(row=2, column=2)
        self.message_queue_entry = tk.Entry(self, width=30)
        self.message_queue_entry.grid(row=3, column=2,  pady=5)
        tk.Button(self, text="Send", command=lambda: self.send_message_queue(self.queue_entry.get(), self.message_queue_entry.get()), width=10, fg="green").grid(row=3, column=3)
        self.queue_log = tk.Text(self, width=30, height=10)
        self.queue_log.grid(row=5, column=2,  pady=5)

class BrokerGUI(tk.Tk,):
    def __init__(self):
        super().__init__()
        self.title("MOM Broker")
        self.geometry("")
        self.queues = []
        self.topics = []


        self.show_main_screen()

    def check_topic(self, topic_name):
        for topic in self.topics:
            if topic[0] == topic_name:
                return True
        return False

    def check_queue(self, queue_name):
        for queue in self.queues:
            if queue[0] == queue_name:
                return True
        return False


    def on_client_send(self, destination):
        if destination.startswith('/queue/'):
            for queue in self.queues:
                if queue[0] == destination[7:]:
                    queue[1] += 1
        elif destination.startswith('/topic/'):
            for topic in self.topics:
                if topic[0] == destination[7:]:
                    topic[1] += 1
        self.update_subscriptions()




    def create_queue(self, queue_name):
        for queue in self.queues:
            if queue[0] == queue_name:
                return
        self.queues.append([queue_name, 0])
        self.update_subscriptions()


    def create_topic(self, topic_name):
        for topic in self.topics:
            if topic[0] == topic_name:
                return
        self.topics.append([topic_name, 0])
        self.update_subscriptions()

    def open_new_window(self):
        ClientGUI(self, str(random.randint(2, 100000000)), self.on_client_send, self.check_topic, self.check_queue)

    def update_subscriptions(self):
        self.e = tk.Entry(self, width=20, fg='blue',
                          font=('Arial', 14, 'bold'))
        self.e.grid(row=3, column=0)
        self.e.insert(tk.END, 'Topic')

        self.e = tk.Entry(self, width=20, fg='blue',
                          font=('Arial', 14, 'bold'))
        self.e.grid(row=3, column=1)
        self.e.insert(tk.END, 'Messages')

        self.e = tk.Entry(self, width=20, fg='green',
                            font=('Arial', 14, 'bold'))
        self.e.grid(row=3, column=2)
        self.e.insert(tk.END, 'Queue')

        self.e = tk.Entry(self, width=20, fg='green',
                            font=('Arial', 14, 'bold'))
        self.e.grid(row=3, column=3)
        self.e.insert(tk.END, 'Messages')



        for i in range(len(self.queues)):
            for j in range(2):
                self.e1 = tk.Entry(self, width=20, fg='blue',
                               font=('Arial', 14))
                self.e1.grid(row=i+4, column=j+2)
                self.e1.insert(tk.END, self.queues[i][j])

        for i in range(len(self.topics)):
            for j in range(2):
                self.e1 = tk.Entry(self, width=20, fg='blue',
                               font=('Arial', 14))
                self.e1.grid(row=i+4, column=j+0)
                self.e1.insert(tk.END, self.topics[i][j])

    def show_main_screen(self):
        self.enter_game_button = tk.Button(self, text="Create Client", command=lambda: self.open_new_window())
        self.enter_game_button.grid(row=0, column=0)

        self.topic_entry = tk.Entry(self, width=30)
        self.topic_entry.grid(row=1, column=0,pady=5)
        tk.Button(self, text="Create Topic", command=lambda: self.create_topic(self.topic_entry.get())).grid(row=2, column=0)

        self.queue_entry = tk.Entry(self, width=30)
        self.queue_entry.grid(row=1, column=2,  pady=5)

        tk.Button(self, text="Create Queue", command=lambda: self.create_queue(self.queue_entry.get())).grid(row=2, column=2)
        self.update_subscriptions()

