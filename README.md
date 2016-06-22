## Traffic Classification & Prioritization

The overall goal of this project is to improve quality of multimedia streaming. This becomes important when other users/applications are downloading large files etc., and it leads to the multimedia quality deterioration. So we first identify the multimedia flow (classification) and then prioritize it. Current Version is 1.0, and it is released on June 22, 2016.

#### Outline
Traffic classification is useful for traffic engineering and network security. Network administrators can use it to allocate, control and manage the network resources as per their requirements. Classification methods can be used to classify P2P traffic, encrypted traffic, web, streaming, download or any specific application.

Our classification model classifies traffic into two classes, i.e., multimedia and download. We used supervised machine learning algorithms ( Decision Tree and K-NN) to build the classification model. This model trained using pre-labeled training instances and later used to classify the traffic in real-time. We use packet level statistics ( average packet size, average inter-arrival time, receiver's window size, flow duration etc.) as  features for ML algorithms.

Prioritization module ensures that once the flow is identified as multimedia it will get higher priority as compared to download flows. We used HTB (Hierarchical Token Bucket Filter) for prioritization.

We have also developed heuristics that can automatically label the data set with some manual inputs, i.e. labeling each flow in the data set as either multimedia or download. These heuristics look at URI of HTTP GET request, and search for multimedia file formats in it, if found then it labels that flow as multimedia.

This project can be used to create a large training data, train the classifier and further classify the traffic. Someone may try to add few new features and change specific setting to analyze the classification behavior.


#### List of modules developed

- Classification module ( 2 approaches, K-NN and decision tree)
- Make Laptop as AP
- Prioritization module (HTB)
- Configure the DHCP server

#### Directory Structure
- **doc**: Contains project documentation
- **scripts**: Contains necessary scripts for the setup

#### Contents ####
- Scripts for various setups, classification and prioritization
- A [user guide](docs/v1.0/README_User.md) containing the setup and installation instructions.
- A [developer guide](docs/v1.0/README_Developer.md) which explains the structure of the scripts.

#### Authors ####
* [Hiren Patel](https://www.linkedin.com/in/hiren-patel-8b310283), Master's student (2014-2016), Dept. of Computer Science and Engineering, IIT Bombay.
	
* [Vidya Sagar Kushwaha](https://in.linkedin.com/in/vidya-sagar-kushwaha-a713a835), Master's student (2014-2016), Dept. of Computer Science and Engineering, IIT Bombay

* [Prof. Mythili Vutukuru](https://www.cse.iitb.ac.in/~mythili/), Dept. of Computer Science and Engineering, IIT Bombay.

#### Contact Us 
- Hiren Patel, hiren131292[AT]gmail.com
- Vidya Sagar Kushwaha, vskushwaha21[AT]gmail.com
- Prof. Mythili Vutukuru, mythili[AT]cse.iitb.ac.in


